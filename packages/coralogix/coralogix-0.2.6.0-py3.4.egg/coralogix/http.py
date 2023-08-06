"""
Implements a low-level client for the Coralogix Web service, along with its data models.
"""
from __future__ import division
from datetime import datetime
from coralogix import config, TICKS_IN_SECOND
from .serialization import Serializable

try: # Python 3
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
    from http.client import UNAUTHORIZED
except ImportError: # Python 2
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
    from httplib import UNAUTHORIZED

try: from enum import Enum
except ImportError: from enum34 import Enum

HTTP_AUTHORIZATION_PROTOCOL = 'bearer'
KEEP_ALIVE_INTERVAL = 10000 # Ten seconds


#
# HTTP Utilities
#

def open_url(url, headers, data):
    """
    High-level interface to `urllib`. Opens the givn URL and returns the HTTP response object.

    :param str url: URL to open.
    :param dict headers: HTTP headers to send along with the request.
    :param int timeout: HTTP request timeout.
    :param bytes data: POST data buffer in the standard application/x-www-form-urlencoded format.
    """
    req = Request(url, data, headers)
    res = urlopen(req, timeout=config.settings.TIMEOUT_IN_MILLI_FOR_REQUESTS / 1000)
    return res


def get(url, headers):
    return open_url(url, headers, None)


def post(url, headers, data):
    return open_url(url, headers, data)


#
# Request and Data Models
#

class AuthRequest(Serializable):
    "Sent to the Coralogix service to establish a new session."

    __serializable__ = (
        ('company_id', 'companyId'),
        ('private_key', None), # Don't serialize, but allow as an instance member
        ('private_key_str', 'privateKey'),
        ('application_name', 'applicationName'),
        ('subsystem_name', 'subsystemName'),
        ('sdk_version', 'version'),
        ('ip_address', 'IPAddress'),
        ('computer_name', 'computerName'),
        ('process_name', 'processName')
    )

    @property
    def private_key_str(self):
        return str(self.private_key)


class Session(AuthRequest):
    "Retains information about the connection with Coralogix."

    __serializable__ = AuthRequest.__serializable__ + (
        ('sdk_id', 'id'),
        ('queue', 'queue'),
        ('token', 'token'),
        ('utc_timestamp', 'GMTTimestamp')
    )


class Log(Serializable):
    "Wraps log entries for sending into a Coralogix queue."

    __serializable__ = (
        ('session', 'sdk'),
        ('serialized_entries', 'logEntries')
    )

    def __init__(self, session, entries):
        self.session = session
        self._entries = entries

    @property
    def serialized_entries(self):
        return [e.serialize() for e in self._entries]

    def __repr__(self):
        return '<{0}: {1} entries>'.format(self.__class__.__name__, len(self._entries))


#
# Coralogix Client
#

class AuthenticationError(Exception):
    pass


class ConnectionStatus(Enum):
    # The user never connected to Coralogix
    NotInitiated = 0
    # There is a valid connection to Coralogix
    Connected = 1
    # The connection with Coralogix was lost
    Disconnected = 2


class Client(object):
    "HTTP client for the Coralogix Web service."

    def __init__(self, api_endpoint):
        self.session = None
        self._url = api_endpoint
        self._headers = {'Content-Type': 'application/json'}
        self._status = ConnectionStatus.NotInitiated
        self._timedelta = None

    @property
    def status(self):
        return self._status

    @property
    def timedelta(self):
        "Returns a timedelta object that represents the difference between the local UTC time and the Coralogix server time."
        return self._timedelta

    def is_connected(self):
        return self._status == ConnectionStatus.Connected

    def authenticate(self, company_id, private_key, app_name, subsystem_name, sdk_version, ip_addr, computer_name, proc_name):
        """
        Establishes a Coralogix service session and retains it within the object.

        :param int company_id: URL to open.
        :param UUID private_key: Private key.
        :param str app_name: Application name.
        :param str subsystem_name: Subsystem name.
        :param str sdk_version: Coralogix SDK version.
        :param str ip_addr: Client IP address.
        :param str computer_name: Client hostname.
        :param str proc_name: Client process name.
        """
        if self.is_connected(): return

        req = AuthRequest(
            company_id=company_id,
            private_key=str(private_key),
            application_name=app_name,
            subsystem_name=subsystem_name,
            sdk_version=sdk_version,
            ip_address=ip_addr,
            computer_name=computer_name,
            process_name=proc_name
        )

        try:
            res = post(self._url, self._headers, req.tojson())
        except URLError as err:
            raise AuthenticationError(err.reason)

        self.session = Session.fromjson(res.read())
        assert self.session.queue.startswith(self._url) # Sanity check
        self.session.private_key = private_key

        if not self.session.token:
            raise AuthenticationError('Connection was refused by Coralogix, please check company ID and private key.')

        self._headers['Authorization'] = '{0} {1}'.format(HTTP_AUTHORIZATION_PROTOCOL, self.session.token)
        self._status = ConnectionStatus.Connected
        self.update_timedelta()

    def handle_error(self, error):
        "Checks if an exception is HTTP 401 and sets the status member accordingly."
        if isinstance(error, HTTPError) and error.code == UNAUTHORIZED:
            self._status = ConnectionStatus.Disconnected

    def update_timedelta(self):
        "Updates the cached difference between local time and Coralogix's server time."
        try:
            res = get(self._url + '/time', self._headers)
        except URLError as err:
            self.handle_error(err)
            raise
        
        local_timestamp = datetime.utcnow()

        ticks = int(res.read()) # Relative to 1970
        server_timestamp = datetime.utcfromtimestamp(ticks / TICKS_IN_SECOND)

        self._timedelta = server_timestamp - local_timestamp

    def post_log(self, entries):
        "Uploads log entries into Coralogix in bulk. `entries` should be an iterable of LogEntry instances."
        log = Log(self.session, entries)
        try:
            res = post(self.session.queue, self._headers, log.tojson())
        except HTTPError as err:
            self.handle_error(err)
            raise AuthenticationError(err.reason)

    def keep_alive(self):
        "Sends a Keep-Alive request to Coralogix so the authorization token won't be revoked."
        try:
            res = post(self._url + '/keep_alive', self._headers, b'')
        except URLError as err:
            self.handle_error(err)
