"""
Implements the Coralogix logger:
a thread-safe class with utilities that allow connecting to the Coralogix service and pushing log entries into it.
"""

from __future__ import division # Get accurate division on Python 2

import socket
import logging
import sys, os, time
from uuid import UUID
from calendar import timegm
from .serialization import Serializable
from datetime import datetime, timedelta
from logging.handlers import MemoryHandler, RotatingFileHandler
from .http import KEEP_ALIVE_INTERVAL, AuthenticationError, Client, ConnectionStatus
from threading import Timer, Lock, current_thread as get_current_thread, active_count as get_thread_count
from coralogix import config, Severity, Category, get_version, CORALOGIX_ENCODING, TICKS_IN_SECOND, MICROSEC_IN_SEC

PSUTIL_ACTIVE = True
try:
    import psutil
except ImportError:
    PSUTIL_ACTIVE = False # TODO: psutil = None

if hasattr(time, 'perf_counter'):
    # Python 3.3 added an accurate cross-platform timer
    timer = time.perf_counter
elif sys.platform == 'win32':
    # On Windows, the best timer is time.clock
    timer = time.clock
else:
    # On most other platforms the best timer is time.time
    timer = time.time

# Define total_seconds() for all python versions:
if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    def total_seconds(timedelta):
        return ((timedelta.days * 86400 + timedelta.seconds) * 10**6 + timedelta.microseconds) / 10**6
else:
    def total_seconds(timedelta):
        return timedelta.total_seconds()

#
# Constants
#

# General
BYTES_IN_KIB = 1024
BYTES_IN_MIB = BYTES_IN_KIB**2
SECOND = 1000 # In milliseconds

# Timing
DEFAULT_TIMER_INTERVAL = SECOND # Normal timer interval in ms

CORALOGIX_LOG_ENTRY_TIMESTAMP_GRANULARITY = timedelta(microseconds=10)

FLUSH_TURBO_ON_THRESHOLD  = 1/2 # Flushing rate will increase if the buffer is half full
FLUSH_TURBO_OFF_THRESHOLD = 1/8 # Flushing rate will be back to normal if the buffer is only one-eighth full

# Internal log
LOG_FILE_NAME = 'CoralogixSDK.log'
LOG_FILE_BUFFER_CAPACITY = 100 # Log records to buffer before flushing them to disk
MAX_LOG_FILE_SIZE = 2 * BYTES_IN_MIB # Internal log will roll-over when it reaches 2 MiB

# Maps Coralogix logging severities to Python logging levels
CORALOGIX_SEVERITY_MAP = {
    Severity.Debug:     logging.DEBUG,
    Severity.Verbose:   logging.DEBUG,
    Severity.Info:      logging.INFO,
    Severity.Warning:   logging.WARNING,
    Severity.Error:     logging.ERROR,
    Severity.Critical:  logging.CRITICAL
}


#
# Utility functions
#

# Add long() in Python 3 to avoid using `six` in `datetime_to_ticks`
if sys.version_info[0] == 3:
    long = int

def datetime_to_ticks(dt):
    """
    Converts the given datetime object to C# ticks. The epoch is 1970.
    Returns an int on Python > 3 or long on lower versions.
    """
    timestamp = timegm(dt.timetuple()) + dt.microsecond / MICROSEC_IN_SEC
    return long(timestamp * TICKS_IN_SECOND)

def _get_buffer_size(log_entries):
    return sum(entry.get_size() for entry in log_entries)


def _get_computer_name():
    return socket.gethostname()


def _get_ip_address():
    return socket.gethostbyname(socket.gethostname())


#
# Classes
#

class LogEntry(Serializable):
    "Represents a single log entry."

    AVERAGE_SIZE = 64

    __serializable__ = (
        ('timestamp_in_ticks', 'timestamp'),
        ('thread_id', 'threadId'),
        ('severity', 'severity'),
        ('category', 'category'),
        ('class_name', 'className'),
        ('method_name', 'methodName'),
        ('message', 'text'),
    )

    def __init__(self, timestamp, thread_id, severity, category, class_name, method_name, message, guid=None, additional_params=None):
        """
        :param datetime timestamp: Log record time
        :param int thread_id: Log producer thread ID
        :param coralogix.Severity severity: Log entry severity
        :param category: Log entry category
        :type category: str or coralogix.Category
        :param str class_name: Log entry producer class name
        :param str method_name: Log entry producer method name
        :param str message: Log entry message
        :param guid: Log entry GUID
        :type guid: str or None
        :param additional_params: Additional parameters for log message. Not used by Coralogix
        :type additional_params: an iterable or None
        """
        self.timestamp = timestamp
        self.thread_id = thread_id
        self.severity = int(severity)

        if isinstance(category, Category):
            category = category.name
        self.category = category

        self.class_name = class_name
        self.method_name = method_name
        self.message = message

        # Not used by Coralogix
        self.guid = guid
        self.additional_params = additional_params

    @property
    def timestamp_in_ticks(self):
        return datetime_to_ticks(self.timestamp)

    def get_size(self):
        "Determines (inaccurately) the size of the entry in bytes."
        return self.AVERAGE_SIZE + len(self.message.encode(CORALOGIX_ENCODING)) # Encode to UTF-8 to get the size in bytes instead of characters


class CoralogixLogger(object):
    #
    # Data members
    #
    _cfg = None
    _buffer = None # Temporary storage for pushed log entries. Initialized in the constructor to avoid sharing the list object among instances
    _timer = None # TODO: implement a periodic timer thread
    _buffer_lock = Lock()
    _buffer_size = 0  # Pre-calculated size (in bytes) of the log buffer
    _drop_severity = 0 # Log entries in this severity and lower might be dropped
    _timer_is_daemon = True # Sets the timer in self._register_timer() to daemon thread
    _logger_handler = None
    _old_settings = None

    #
    # Timing members
    #
    _last_timer = 0
    _elapsed_time = 0 # Counts milliseconds since last successful connection
    _last_entry_timestamp = None

    _reconnection_interval = 0
    _flush_log_interval = 0
    _flush_log_turbo_on = False # Is the flushing set on turbo mode?
    _log_perf_data_interval = 0

    #
    # Statistics
    #

    # Log queue stats
    _total_log_entries_pushed = 0
    _total_log_entries_sent = 0
    _total_log_entries_dropped = 0

    # Connection stats
    _last_connection_time = None
    _last_disconnection_time = None
    _consecutive_auth_failures = 0
    _consecutive_flush_failures = 0


    def __init__(self, config_dir=None, log_dir=None):
        self._config_dir = config_dir or os.getcwd()

        self._client = Client(config.settings.CORALOGIX_API_ENDPOINT) # Coralogix HTTP client

        self._init_logger(log_dir or self._config_dir) # If unspecified, use the same location as the configuration file

        self._buffer = [] # Ensures each class instance gets a new list object

        # Set initial timing values
        self._flush_log_interval     = config.settings.BULK_TIME_IN_MILLI_THRESHOLD
        self._log_perf_data_interval = config.settings.LOG_PERFORMANCE_DATA_INTERVAL

        # Start the timer immediately
        self._register_timer(DEFAULT_TIMER_INTERVAL)

    def close(self):
        try:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

            self._send_inner_log(Severity.Info, 'The user has called the close method. The Python SDK will terminate and stop sending logs')
            self._async_push_log() # best effort
            self.__class__._logger_handler.flush()
        except:
            self._logger.exception('Error:')
    
    def __del__(self):
        self.close()

    def _init_logger(self, path):
        "Internal logger setup."
        if config.settings.IS_PRODUCTION_MODE:
            self.__class__._logger_handler = logging.NullHandler()
        else:
            try:
                log_file_handler = RotatingFileHandler(os.path.join(path, LOG_FILE_NAME), maxBytes=MAX_LOG_FILE_SIZE, backupCount=1)
            except IOError:
                log_file_handler = logging.StreamHandler()
            log_file_formatter = logging.Formatter('%(asctime)s\t%(threadName)s\t%(levelname)s\t%(funcName)s\t%(message)s')
            log_file_handler.setFormatter(log_file_formatter)

            self.__class__._logger_handler = MemoryHandler(LOG_FILE_BUFFER_CAPACITY, target=log_file_handler)

        self._logger = logging.getLogger(self.__class__.__name__) # Internal logger. Does not log to Coralogix!
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False
        self._logger.addHandler(self.__class__._logger_handler)

    @property
    def sdk_version(self):
        return get_version()

    def connect(self, company_id, private_key, application_name=None, subsystem_name=None, raise_exceptions=True):
        """
        Connects the SDK to Coralogix by authenticating and retaining an authorization token (does not keep an open socket).
        If authentication failed due to a network problem, it will be tried again, up to the configurable retry limit.
        """
        error_msg = None
        private_key_uuid = None
        rv = False

        try:
            self._logger.info('The connect method was called for the Application %r, Subsystem %r and Company %r', application_name, subsystem_name, company_id)

            # Normalize application and subsystem names
            if application_name is None:
                application_name = config.settings.APPLICATION_NAME

            if subsystem_name is None:
                subsystem_name = config.settings.SUBSYSTEM_NAME

            # Fail-safe in case the application and subsystem names were not defined in configuration
            if not application_name:
                application_name = 'NO_APPLICATION_NAME'
                self._logger.warning('The connect method was called with an empty Application name')

            if not subsystem_name:
                subsystem_name = 'NO_SUBSYSTEM_NAME'
                self._logger.warning('The connect method was called with an empty Subsystem name')

            # Validate private key as a GUID
            try:
                private_key_uuid = private_key if isinstance(private_key, UUID) else UUID(private_key)
            except ValueError:
                self._logger.error('The private key specified is invalid')

                if raise_exceptions:
                    error_msg = 'The private key specified is invalid. It should be a GUID or a string that can be parsed as a GUID.'

            # Initiate a connection only if not already connected
            if private_key_uuid:
                if not self._client.is_connected():
                    try:
                        self._authenticate(company_id, private_key_uuid, application_name, subsystem_name)
                    except AuthenticationError as err:
                        error_msg = str(err)

                    if self._client.is_connected():
                        self._last_timer = timer()
                        self._last_connection_time = datetime.utcnow()
                        self._logger.debug('The SDK is now connected to Coralogix')

                        if config.settings.IS_ACTIVE:
                            self._send_inner_log(Severity.Verbose, self._get_formatted_config(False))
                            self._logger.debug('Internal SDK configuration was pushed to Coralogix')

                        rv = True
                    else:
                        self._logger.error('The SDK could not connect to Coralogix')
                else:
                    self._logger.warning('The connect method was called but Coralogix SDK is already connected')

        except Exception as err:
            self._logger.exception('The SDK could not connect to Coralogix. Error details:')
            if raise_exceptions:
                error_msg = 'The SDK could not connect to Coralogix. Error details:\n{0}'.format(err)
        finally:
            if error_msg and raise_exceptions:
                raise Exception(error_msg)
            return rv

    def _get_timestamp(self):
        "Returns the current server UTC timestamp as a datetime object."
        return datetime.utcnow() + self._client.timedelta

    def send_log(self, severity, msg, category=Category.General, class_name=None, method_name=None):
        """
        Queues a log entry for sending out to Coralogix.

        :param Severity severity: Entry severity.
        :param str msg: Log entry message.
        :param category: Log entry category. If unspecified, defaults to "General".
        :type category: str or coralogix.Category
        :param class_name: Log entry producer class. Can be left unspecified.
        :param method_name: Log entry producer method. Can be left unspecified.
        """
        return self._push_entry(self._get_timestamp(), severity, category, class_name, method_name, msg)

    def _send_inner_log(self, severity, msg):
        "Logs an internal SDK message to Coralogix."
        return self.send_log(severity, msg, 'CORALOGIX')

    def _push_entry(self, timestamp, severity, category, class_name, method_name, msg, additional_params=None):
        """
        Queues a log entry for sending out to Coralogix (internal method).
        Does nothing if the SDK has never connected to Coralogix or if it isn't active.
        Returns True if the entry has been successfully queued for sending, False otherwise.
        """
        if self._client.status == ConnectionStatus.NotInitiated or not config.settings.IS_ACTIVE:
            return False

        if not isinstance(severity, Severity):
            self._logger.warning('Log entry was pushed with an invalid severity: %r. Converting to Verbose', severity)
            severity = Severity.Verbose

        try:
            entry = LogEntry(timestamp, get_current_thread().ident, severity, category, class_name, method_name, msg, None, additional_params)

            with self._buffer_lock:
                self._buffer.append(entry)
                self._buffer_size += entry.get_size()
                self._total_log_entries_pushed += 1
            return True
        except Exception:
            self._logger.exception('Error:')
            return False

    def _log_event(self, severity, message):
        "Logs a message both to Coralogix and to the local file."
        self._send_inner_log(severity, message)
        self._logger.log(CORALOGIX_SEVERITY_MAP.get(severity, logging.NOTSET), message)

    def _authenticate(self, company_id, private_key, application_name, subsystem_name):
        "Tries to authenticate the Coralogix client until the failure count reaches the configured limit."
        tries = 0
        try:
            ip = _get_ip_address()
        except Exception:
            ip = "NO_IP_NAME"
        try:
            computer = _get_computer_name()
        except Exception:
            computer = "NO_COMPUTER_NAME"
        if PSUTIL_ACTIVE is True:
            procname = psutil.Process().name()
        else:
            procname = "NO_PROCESS_NAME"

        while not self._client.is_connected() and tries < config.settings.AUTHENTICATION_RETRIES:
            self._logger.debug('Trying to authenticate application %s and subsystem %s', application_name, subsystem_name)

            try:
                self._client.authenticate(company_id, private_key, application_name, subsystem_name, self.sdk_version, ip, computer, procname)
            except AuthenticationError:
                self._logger.exception('Error:')
                raise # Error is related to private key. No point in retrying...
            except Exception:
                self._consecutive_auth_failures += 1
                self._logger.exception('Error:')
                time.sleep(config.settings.INTERVAL_IN_MILLI_TO_SLEEP_BETWEEN_RETRIES / 1000)

    def _get_formatted_config(self, is_reloading):
        "Returns a formatted string that represents the current SDK configuration."
        app_name = self._client.session.application_name  #config.settings.APPLICATION_NAME if config.settings.APPLICATION_NAME else 'EMPTY'
        subsystem_name = self._client.session.subsystem_name  #config.settings.SUBSYSTEM_NAME if config.settings.SUBSYSTEM_NAME else 'EMPTY'
        
        lines = []
        if is_reloading:
            lines.append('The configuration values just changed to:')
            lines.append('Application Name = {0}'.format(app_name))
            lines.append('Subsystem Name = {0}'.format(subsystem_name))
        else:
            lines.append('The Application Name {0} and Subsystem Name {1} from the Python SDK have begun sending data with the following configuration parameters:'.format(app_name, subsystem_name))

        # Add all settings that weren't already added
        [lines.append('{0} = {1}'.format(k, v)) for k, v in config.as_dict().items() if k != 'APPLICATION_NAME' and k != 'SUBSYSTEM_NAME']
        return os.linesep.join(lines)

    def _register_timer(self, interval):
        "Initiates a new timer thread in place of the current one (if exists) and starts it right away. Interval should be specified in milliseconds."
        self._timer = None # Dispose of a previous timer
        self._timer = Timer(interval / SECOND, self._on_timer_elapsed)
        self._timer.daemon = self._timer_is_daemon
        self._timer.start()

    def _reload_config(self):
        "Reloads the configuration from file. If it changed, sends the new configuration to Coralogix and saves them to the local log."
        try:
            config.reload_settings()
            new_settings = config.as_dict()
    
            if self._old_settings is not None and new_settings != self._old_settings: # Comparison is possible because config.as_dict() returns an OrderedDict
                # IS_PRODUCTION_MODE changes are not handled!
                self._logger.info('Configuration changed')
                self._log_event(Severity.Verbose, self._get_formatted_config(True)) # Inform Coralogix of the new settings
    
            self._old_settings = new_settings
        except Exception:
            self._logger.exception("Could not reload the config settings:")

    def _on_timer_elapsed(self):
        try:
            self._timer.cancel() # Stop the timer until we are finished

            # Count the elapsed time to check which methods should be called right now
            self._elapsed_time += (timer() - self._last_timer) * SECOND # Convert to milliseconds
            self._last_timer = timer()

            # Reload all configuration values?
            if self._elapsed_time % config.settings.RELOAD_CONFIG_INTERVAL < SECOND:
                self._reload_config()

            # Is the SDK active?
            if config.settings.IS_ACTIVE:
                if self._elapsed_time % config.settings.BULK_TIME_IN_MILLI_THRESHOLD < SECOND and self._client.status != ConnectionStatus.NotInitiated:
                    self._drop_records_if_needed()

                # The MemoryHandler flushes on its own when its buffer fills; We also flush it explicitly when enough time has passed
                if self._elapsed_time % config.settings.INTERVAL_IN_MILLI_TO_FLUSH_LOCAL_LOG < SECOND:
                    self.__class__._logger_handler.flush()

                # Are we currently connected to Coralogix?
                if self._client.is_connected():
                    # Should we synchronize local time with server time?
                    if self._elapsed_time % config.settings.INTERVAL_IN_MILLI_TO_SYNC_CORALOGIX_TIME < SECOND:
                        try:
                            self._client.update_timedelta()
                            self._logger.debug('Updated delta between server and local times to: %fs', total_seconds(self._client.timedelta));
                        except:
                            self._logger.exception('Could not parse server response to a valid time:')

                    # If enough time passed or if the buffer size is big enough
                    if self._elapsed_time % self._flush_log_interval < SECOND and len(self._buffer) > 0 \
                        or self._buffer_size > config.settings.BULK_SIZE_IN_KIB_THRESHOLD * BYTES_IN_KIB:
                        self._async_push_log()

                    if self._elapsed_time % KEEP_ALIVE_INTERVAL < SECOND:
                        try:
                            self._client.keep_alive()
                        except Exception:
                            self._logger.exception("Could not signal keep alive with the server")

                    # Should we send inner data?
                    if self._elapsed_time % self._log_perf_data_interval < SECOND:
                        self._log_perf_data()
                elif self._client.status == ConnectionStatus.Disconnected:
                    if self._elapsed_time % self._reconnection_interval < SECOND:
                        self._reconnect() # No exception handling
            else: # Not active
                self._logger.debug('SDK INACTIVE')
        except Exception as err:
            if isinstance(err, AuthenticationError) and self._client.status == ConnectionStatus.Disconnected:
                self._handle_token_revocation()
            else:
                self._logger.exception('Error:')
        finally:
            try:
               self._register_timer(self._timer.interval * SECOND) # Restart the timer thread with the same interval
            except Exception:
                self._logger.critical('In finally scope. Timer cannot be started! Exception details:')
                self._logger.exception()

    def _log_perf_data(self):
        "Logs application performance data to Coralogix."
        try:
            if PSUTIL_ACTIVE is True:
                cpu_usage = psutil.cpu_percent()
                mem_usage = psutil.virtual_memory().percent
            else:
                cpu_usage = -1
                mem_usage = -1
            connection_duration = datetime.utcnow() - self._last_connection_time

            log_parts = [
                'Monitoring performance for Application: {0}'.format(self._client.session.application_name),
                'for Subsystem: {0}'.format(self._client.session.subsystem_name),
                'from IP: {0}'.format(_get_ip_address()),
                'CPU Usage: {0}'.format(cpu_usage),
                'Memory Consumption: {0}'.format(mem_usage),
                'Thread count: {0}'.format(get_thread_count()),
                'Time active: {0}s'.format(total_seconds(connection_duration)),
                'Total log entries sent: {0}'.format(self._total_log_entries_sent)
            ]

            # Ensure that once the data's been pushed, the dynamic value will return to its normal value.
            # It might also change as user changes the configuration
            self._log_perf_data_interval = config.settings.LOG_PERFORMANCE_DATA_INTERVAL

            self._send_inner_log(Severity.Verbose, ' | '.join(log_parts))
        except Exception:
            # Set the dynamic interval to the maximum value allowed in order to avoid too many execptions
            self._log_perf_data_interval = config.constraints.MAX_LOG_PERFORMANCE_DATA_INTERVAL
            
            self._logger.exception('Error:')
            try:
                self._send_inner_log(Severity.Info, 'The Python SDK has encountered a problem when trying to gather process parameters.\n'
                    'No such attempts will be made for a duration of: {0} seconds'.format(self._log_perf_data_interval / 1000))
            except:
                self._logger.exception('Inner Error:')

    def _async_push_log(self):
        try:
            self._logger.debug('Entering _async_push_log. Preparing the bulk that will be sent to Coralogix')

            with self._buffer_lock:
                temp_buffer_size = self._buffer_size

            bulk_size_in_bytes_threshold = config.settings.BULK_SIZE_IN_KIB_THRESHOLD * BYTES_IN_KIB

            if temp_buffer_size > bulk_size_in_bytes_threshold:
                # Insert some items back into the buffer in order to send a smaller bulk
                with self._buffer_lock:
                    temp_buffer_size = self._buffer_size
                    total_entries_to_send = int(len(self._buffer) * bulk_size_in_bytes_threshold / temp_buffer_size)

                    # Ensure that at least 10% of the messages will be sent regardless of maximum bulk size
                    if total_entries_to_send <= len(self._buffer) / 10:
                        total_entries_to_send = int(len(self._buffer) / 10 + 1)

                    temp_buffer = self._buffer[0:total_entries_to_send]
                    del self._buffer[0:total_entries_to_send]
                    self._buffer_size -= bulk_size_in_bytes_threshold

                self._logger.debug('Buffer size is %d bytes, which is greater than %d bytes. Moved %d entries from the buffer to a temporary buffer. '
                                    'The buffer still has %d entries and its size is %d bytes',
                                    temp_buffer_size, bulk_size_in_bytes_threshold, len(temp_buffer), len(self._buffer), self._buffer_size)
            else:
                # Move the log entries to a temporary local buffer in order to send it entirely
                with self._buffer_lock:
                    temp_buffer = self._buffer
                    self._buffer = []
                    temp_buffer_size = self._buffer_size
                    self._buffer_size = 0

                self._logger.debug('Buffer size is correct and can be sent entirely. Moved %d entries from the buffer to a temporary buffer. '
                                    'Total size is %d bytes', len(temp_buffer), temp_buffer_size)

            self._validate_log_timestamps(temp_buffer)

            # TODO: use a context manager (`with Timer() as timer: ...`)
            start_time = timer()
            flush_succeeded = self._flush_log_buffer(temp_buffer)
            elapsed_ms = (timer() - start_time) * SECOND

            if flush_succeeded:
                self._logger.debug('The buffer of %d entries was sent after %dms', len(temp_buffer), elapsed_ms)
            else:
                self._logger.error('The buffer of %d entries was not sent after %dms', len(temp_buffer), elapsed_ms)
        except Exception:
            self._logger.exception('Error:')

        self._logger.debug('Leaving _async_push_log. Buffer count is %d', len(self._buffer))

    def _flush_log_buffer(self, log_entries):
        "Sends the buffered log entries out to Coralogix. Reconnects with Coralogix if needed."
        try:
            self._client.post_log(log_entries)

            if self._consecutive_flush_failures > 0:
                self._send_inner_log(Severity.Info, 'Coralogix SDK has disconnected from its server BUT managed to reconnect')
                self._logger.info('Coralogix SDK has successfully reconnected to its server. Consecutive flush failures: %d', self._consecutive_flush_failures)
                self._consecutive_flush_failures = 0

            prev_timer_interval = self._timer.interval * SECOND
            if prev_timer_interval != DEFAULT_TIMER_INTERVAL:
                self._timer.cancel()
                self._register_timer(DEFAULT_TIMER_INTERVAL)
                self._logger.info('Timer interval has been reset to its normal %dms value (was %dms)', DEFAULT_TIMER_INTERVAL, prev_timer_interval)

            self._logger.debug('The buffer of size %d was sent correctly', len(log_entries))

            self._total_log_entries_sent += len(log_entries)

            self._logger.debug(
                'The number of sent messages was increased to %d. The number of received messages is %d. The number of dropped messages is %d',
                self._total_log_entries_sent, self._total_log_entries_pushed, self._total_log_entries_dropped
            )

            return True
        except Exception as err:
            try:
                with self._buffer_lock:
                    # Insert the entries back into the buffer
                    self._buffer = log_entries + self._buffer
                    self._buffer_size = _get_buffer_size(self._buffer)

                self._logger.exception('Error:')
                self._logger.warning('The log entries were inserted back into the log buffer')

                # If the request was unauthorized, we don't have a valid token anymore, and we need to re-authenticate
                if isinstance(err, AuthenticationError) and self._client.status == ConnectionStatus.Disconnected:
                    self._handle_token_revocation()
                else:
                    self._consecutive_flush_failures += 1

                    if self._consecutive_flush_failures == config.settings.FLUSH_RETRIES:
                        self._timer.cancel()
                        self._register_timer(config.settings.INTERVAL_IN_MILLI_FOR_TIMER_ON_DISCONNECTION)
                        self._logger.warning('Due to consecutive connection failures, timer interval was changed to %dms', config.settings.INTERVAL_IN_MILLI_FOR_TIMER_ON_DISCONNECTION)
            except Exception:
                self._logger.exception('Inner exception:')

            return False

    def _handle_token_revocation(self):
        self._logger.error('Coralogix SDK has lost its token and thus the server has disconnected the session -> trying to establish connection')
        self._last_disconnection_time = datetime.utcnow()
        self._reconnection_interval = config.settings.INTERVAL_IN_MILLI_TO_START_TRYING_TO_RECONNECT
        self._total_log_entries_dropped = 0
        self._consecutive_auth_failures = 0
        self._log_event(Severity.Info, 'Coralogix SDK has disconnected from its server')

    def _drop_records_if_needed(self):
        "Checks if the buffer is larger than it's allowed size, and drops records as needed."
        try:
            with self._buffer_lock:
                temp_buffer_size = self._buffer_size
                temp_buffer_count = len(self._buffer)

            self._logger.info('Validating buffer size, which is %d bytes (buffer count is %d)', temp_buffer_size, temp_buffer_count)

            buffer_max_size_in_bytes = config.settings.BUFFER_MAX_SIZE_IN_KIB * BYTES_IN_KIB

            if temp_buffer_size > buffer_max_size_in_bytes: # If the buffer size exceeds the maximum allowed
                with self._buffer_lock:
                    temp_buffer = self._buffer
                    self._buffer = []
                    temp_buffer_size = self._buffer_size
                    self._buffer_size = 0

                self._logger.info('Too many logs in the buffer. Its size is %d bytes but we allow a maximum of %d bytes. '
                    'We moved them to a temporary buffer and we will reduce it', temp_buffer_size, buffer_max_size_in_bytes)

                # Until we don't need to drop anymore
                while temp_buffer_size > buffer_max_size_in_bytes:
                    if self._drop_severity < max(Severity):
                        self._drop_severity += 1

                    messages_before_dropping = len(temp_buffer)

                    # If we are not at the last level of dropping, we filter the log entries normally
                    if self._drop_severity < max(Severity):
                        self._logger.info('We will drop everything up to severity %d', self._drop_severity)
                        temp_buffer = [entry for entry in temp_buffer if entry.severity > self._drop_severity]
                    # Dropping so far was not enough, therefore we filter all the log entries up to level 5, and half of the remaining ones.
                    else:
                        self._logger.warning('We will drop everything up to Error and then we will drop half of the remaining Critical logs')
                        temp_buffer = [entry for entry in temp_buffer if entry.severity == Severity.Critical]
                        del temp_buffer[0:int(len(temp_buffer) / 2)]

                    dropped_messages_count = messages_before_dropping - len(temp_buffer)
                    self._total_log_entries_dropped += dropped_messages_count

                    self._logger.info('Dropped %d messages. The temporary buffer was reduced to %d entries', dropped_messages_count, len(temp_buffer))

                    temp_buffer_size = _get_buffer_size(temp_buffer)

                self._log_event(Severity.Info,
                    'Internal message buffer has reached its maximum limit of {0} KiB, log entries from the Severity {1} and below will be dropped and will not be sent to Coralogix'.format(
                        config.settings.BUFFER_MAX_SIZE_IN_KIB, Severity(self._drop_severity).name
                    )
                )
                
                self._logger.info('We will reinsert the temporary buffer back into the buffer')
                # Insert everything back into the buffer
                with self._buffer_lock:
                    self._buffer = temp_buffer + self._buffer
                    self._buffer_size += temp_buffer_size

            # Or if we need to stop dropping
            else:
                # If the buffer size is fine but we were dropping messages, reset the severity threshold
                if temp_buffer_size < config.settings.BUFFER_MAX_SIZE_IN_KIB * BYTES_IN_KIB * config.settings.PERCENTAGE_OF_BUFFER_NORMAL_COMPLETENESS / 100 \
                    and self._drop_severity > 0:
                    self._logger.debug('Buffer is now normal, we suspend the dropping of messages as its size is %d bytes', temp_buffer_size)

                    self._drop_severity = 0

                    self._log_event(Severity.Info, 'Internal message buffer is back to its normal values. From now on, all log entries will be sent to Coralogix. '
                        'A total of {0} messages were lost since the beginning of the logging'.format(self._total_log_entries_dropped))

                # If the buffer is at least half full, the rate of sending logs should increase
                if self._client.is_connected() and self._timer.interval != config.settings.INTERVAL_IN_MILLI_FOR_TIMER_ON_DISCONNECTION:
                    # Buffer full enough; increase rate
                    if not self._flush_log_turbo_on and temp_buffer_size >= buffer_max_size_in_bytes * FLUSH_TURBO_ON_THRESHOLD:
                        self._flush_log_turbo_on = True
                        self._register_timer(config.constraints.MIN_BULK_TIME_IN_MILLI_THRESHOLD)
                        self._flush_log_interval = config.constraints.MIN_BULK_TIME_IN_MILLI_THRESHOLD
                        self._logger.info('Buffer is half full -> increasing send rate to every %dms', config.constraints.MIN_BULK_TIME_IN_MILLI_THRESHOLD)
                    # Buffer empty enough; decrease rate
                    elif self._flush_log_turbo_on and temp_buffer_size < buffer_max_size_in_bytes * FLUSH_TURBO_OFF_THRESHOLD:
                        self._flush_log_turbo_on = False
                        self._register_timer(DEFAULT_TIMER_INTERVAL)
                        self._logger.info('Buffer size is back to normal -> return regular send rate value. Buffer size is: %d bytes', temp_buffer_size)
                    elif not self._flush_log_turbo_on:
                        # Buffer size is normal; ensure values are up to date with the configuration
                        self._flush_log_interval = config.settings.BULK_TIME_IN_MILLI_THRESHOLD

        except Exception:
            self._logger.exception('Error:')

    def _validate_log_timestamps(self, temp_buffer):
        """
        Coralogix requires log entries to have unique timestamps. This method ensures the following:
         - No two successive log entries have the same timestamp;
         - No log entry has a timestamp that precedes its predecessor;
         - No log entry is more than 10 seconds in the future, relative to the Coralogix server time.
        """
        try:
            for entry in temp_buffer:
                # The entry timestamp should be greater than the timestamp of the entry before it
                if self._last_entry_timestamp is not None and entry.timestamp <= self._last_entry_timestamp:
                    entry.timestamp = self._last_entry_timestamp + CORALOGIX_LOG_ENTRY_TIMESTAMP_GRANULARITY

                # If entry is more than 10s in the future - reset its timestamp
                if total_seconds(entry.timestamp - self._get_timestamp()) > 10:
                    self._last_entry_timestamp = self._get_timestamp()
                else:
                    self._last_entry_timestamp = entry.timestamp
        except Exception:
            self._logger.exception('Error:')

    def _reconnect(self):
        succeeded = self.connect(
            self._client.session.company_id,
            self._client.session.private_key,
            self._client.session.application_name,
            self._client.session.subsystem_name,
            False  # Don't raise exceptions!
        )

        if not succeeded:
            # Increase the interval until trying again
            self._reconnection_interval = config.settings.INTERVAL_IN_MILLI_FOR_TIMER_ON_DISCONNECTION
            self._logger.error('Couldn\'t connect. Increased the reconnection retries to %d and the interval to try a new reconnection to %d', self._consecutive_auth_failures, self._reconnection_interval)
        else:
            # Now that we reconnected, inform Coralogix of the disconnection
            disconnect_duration = datetime.utcnow() - self._last_disconnection_time
            log_parts = (
                'Coralogix SDK has disconnected from its server BUT managed to reconnect, disconnection time {0}'.format(total_seconds(disconnect_duration) * SECOND), # Milliseconds, as in the C# SDK
                'number of retries {0}'.format(self._consecutive_auth_failures),
                'messages lost {0}'.format(self._total_log_entries_dropped)
            )
            self._log_event(Severity.Info, ' | '.join(log_parts))
