
import sys
import time
import json
import logging
import threading
from logging import Handler

try:  # Python 3 imports and functions
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
    from http.client import UNAUTHORIZED
    from queue import Queue, Empty

except ImportError:  # Python 2 imports and functions
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
    from httplib import UNAUTHORIZED
    from Queue import Queue, Empty

try:
    from enum34 import Enum, IntEnum
except ImportError:  # Python 2 import enum:
    from enum import Enum, IntEnum
    
if sys.version_info[0] == 2:
    from threading import _Timer as Timer
else:
    from threading import Timer


class Severity(IntEnum):
    Debug = 1
    Verbose = 2
    Info = 3
    Warning = 4
    Error = 5
    Critical = 6

VERBOSE = 15
logging.addLevelName(VERBOSE, 'VERBOSE')


#
# Maps Python logging levels to Coralogix severities
#
LOGGING_LEVEL_MAP = {
    logging.DEBUG:      Severity.Debug,
    VERBOSE:            Severity.Verbose,
    logging.INFO:       Severity.Info,
    logging.WARNING:    Severity.Warning,
    logging.ERROR:      Severity.Error,
    logging.CRITICAL:   Severity.Critical
}


class DaemonTimer(Timer, object):
    """
    A threading.Timer object which is automatically set to self.daemon=True
    """
    def __init__(self, interval, function, *args, **kwargs):
        super(DaemonTimer, self).__init__(interval, function, *args, **kwargs)
        self.daemon = True


class CoralogixHTTPSHandler(Handler, object):

    # Additional future features:
    # 1. use priority queue to send high severity logs first
    # Server timedelta parameters:
    _get_time_url = 'https://api.coralogix.com/sdk/v1/time'  # URL to get server timedelta
    _check_timedelta_time_interval = 600  # Time interval in seconds for updating the timedelta from the server
    # POST command parameters:
    _post_url = "https://api.coralogix.com/api/v1/logs"  # Coralogix URL for http-post requests
    _post_headers = {"Content-Type": "application/json"}
    _post_timeout = 5  # Timeout in seconds for http-post requests
    _post_max_log_entries = 2000  # Maximum log entries inside each bulk POST command
    
    # Trigger send_log parameters:
    _post_time_interval = 5  # Time interval in seconds for triggering a POST command
    # _log_count_trigger = 1000  # Min log count in queue for triggering a POST command
    _log_count_trigger = 1000  # Min log count in queue for triggering a POST command
    _check_count_time_interval = 1  # Time interval between consecutive log count checks

    def __init__(self, company_id, private_key, application, subsystem, computer_name=None, post_url=None, silence_exceptions=True):
        """
        If silence_exceptions is True, exceptions will be silenced when encountered.
        :param company_id: int
        :param private_key: str
        :param application: str
        :param subsystem: str
        :param silence_exceptions: bool
        """
        super(CoralogixHTTPSHandler, self).__init__()
        self._exception_formatter = logging.Formatter().formatException
        self._post_url = post_url or self._post_url
        # Coralogix Parameters:
        self.company_id = company_id
        self.private_key = private_key
        self.application = application
        self.subsystem = subsystem
        self.computer_name = computer_name
        # Log variables:
        self.queue = Queue()
        self.received_logs_counter = 0
        self.sent_logs_counter = 0
        self.server_timedelta = 0  # Timedelta in milliseconds to add to logs for server sync
        # Exceptions handling:
        self.silence_exceptions = silence_exceptions
        # Timers and triggers
        self.__trigger_send = threading.Event()  # Event for triggering a send log event
        self.__trigger_stop = threading.Event()  # Event for gracefully stopping the handler
        self.__time_timer = self.time_timer_factory()  # Timer which triggers self._trigger_send()
        self.__count_timer = self.count_timer_factory()  # Timer which runs self.trigger_by_log_num()
        self.__update_timdelta_timer = self.timedelta_timer_factory(0.01)  # Timer for updating the server timedelta (immediately)
        self.__time_timer.start()
        self.__count_timer.start()
        self.__update_timdelta_timer.start()
        # Activate send_logs()
        self.send_logs_thread = threading.Thread(target=self.send_logs)
        self.send_logs_thread.daemon = False  # Prevents the thread from closing before the buffer is empty
        self.send_logs_thread.start()

    def emit(self, record):
        try:
            # Format the message:
            log_entry = dict()
            timestamp = record.__dict__.get("override_timestamp") or record.created
            log_entry["timestamp"] = timestamp * 1e3 + self.server_timedelta
            log_entry["severity"] = self.convert_severity(record.levelno).value
            log_entry["category"] = record.name
            log_entry["className"] = record.filename
            log_entry["methodName"] = record.funcName
            log_entry["threadId"] = record.thread
            log_entry["text"] = record.getMessage()
            if record.exc_info and record.exc_info[0] and record.exc_info[1] and record.exc_info[2]:
                # Add exception info:
                try:
                    exception_text = self._exception_formatter(record.exc_info)
                    log_entry["text"] += "\n" + exception_text
                except Exception:
                    pass
            # JSON encode, queue and count:
            self.queue.put_nowait(log_entry)
            self.received_logs_counter += 1
        except Exception:
            self.handleError(record)

    def send_logs(self):
        while not (self.__trigger_stop.is_set() and self.queue.empty()):
            self.__trigger_send.wait()
            # Stop timers:
            self.__count_timer.cancel()
            self.__time_timer.cancel()
            # Send logs:
            try:
                if not self.queue.empty():
                    # Main post message body:
                    post_message = dict(privateKey=self.private_key,
                                        applicationName=self.application,
                                        subsystemName=self.subsystem,
                                        logEntries=list())
                    if self.computer_name:  # Add computer_name if it exists:
                        post_message["computerName"] = self.computer_name
                    # Add log records:
                    log_entries_count = 0
                    log_entries = list()
                    while not self.queue.empty() and log_entries_count < self._post_max_log_entries:
                        try:
                            log_message = self.queue.get_nowait()
                            log_entries.append(log_message)
                            log_entries_count += 1
                        except Empty:
                            pass
                    if log_entries_count > 0:
                        post_message["logEntries"] = log_entries
                        # Encode and send:
                        json_message = json.dumps(post_message).encode('UTF-8')
                        response = self.post(json_message)
                        if response is not None and 199 < response.getcode() < 400:
                            self.sent_logs_counter += log_entries_count
            except Exception as e:
                if self.silence_exceptions is False:
                    raise
            # Create new timers and start them:
            if self.trigger_by_log_num_condition():  # Re-run the count test in case we had more than self._post_max_log_entries logs in the queue
                continue
            self.__count_timer = self.count_timer_factory()
            self.__time_timer = self.time_timer_factory()
            self.__trigger_send.clear()
            self.__count_timer.start()
            self.__time_timer.start()

    @staticmethod
    def convert_severity(python_severity):
        """
        Converts Python's Logging severity level to Coralogix' severity level.
        :param python_severity: int
        :return: int
        """
        level = LOGGING_LEVEL_MAP.get(python_severity)
        if level is None:
            level = LOGGING_LEVEL_MAP[min(LOGGING_LEVEL_MAP, key=lambda x: abs(x-python_severity))]
        return level
    
    def get_server_timedelta(self):
        """ Updates self.server_timedelta """
        # Cancel and delete old timer
        self.__update_timdelta_timer.cancel()
        del self.__update_timdelta_timer
        # Update timedelta
        server_time = None
        for i in range(3):  # Retry 3 times re retrieve server timestamp:
            try:
                server_time = int(self.post(None, self._get_time_url).read()) / 1e4  # Server time in milliseconds
                local_time = time.time() * 1e3  # Local time in milliseconds
                if server_time:
                    self.server_timedelta = server_time - local_time
                    break
            except Exception:
                continue
        # Create new timer
        self.__update_timdelta_timer = self.timedelta_timer_factory()
        self.__update_timdelta_timer.start()
        
    def post(self, data, url=None):
        response = None
        url = url or self._post_url
        try:
            request = Request(url, data, self._post_headers)
            response = urlopen(request, timeout=self._post_timeout)
        except Exception as e:
            if self.silence_exceptions is False:
                print("CoralogixHTTPSHandler.post(): caught exception= {0}".format(e))
        return response

    # Timer factory methods:
    def time_timer_factory(self, time_interval=None):
        """
        Returns a DaemonTimer which sets self._trigger_send Event every self._post_time_interval seconds.
        :param time_interval: float
        """
        time_interval = time_interval or self._post_time_interval
        return DaemonTimer(time_interval, self._trigger_send)

    def count_timer_factory(self, time_interval=None):
        """
        Returns a DaemonTimer which runs self.trigger_by_log_num() every self._check_count_time_interval.
        :param time_interval: float
        """
        time_interval = time_interval or self._check_count_time_interval
        return DaemonTimer(time_interval, self.trigger_by_log_num)
    
    def timedelta_timer_factory(self, time_interval=None):
        """
        Returns a DaemonTimer which runs self.trigger_by_log_num() every self._check_count_time_interval.
        :param time_interval: float
        """
        time_interval = time_interval or self._check_timedelta_time_interval
        return DaemonTimer(time_interval, self.get_server_timedelta)
    
    # Trigger methods:
    def trigger_by_log_num(self):
        """
        Triggers self.__trigger_send if number of logs exceeds self._log_count_trigger
        """
        try:
            if self.trigger_by_log_num_condition():
                self._trigger_send()
            else:
                self.__count_timer = self.count_timer_factory()
                self.__count_timer.start()
        except Exception as e:
            print("trigger_by_log_num(): caught exception= {0}".format(e))

    def trigger_by_log_num_condition(self):
        return self._log_count_trigger <= self.queue.qsize()

    def flush(self):
        self._trigger_send()
        self._trigger_stop()

    def _trigger_send(self):
        self.__trigger_send.set()

    def _trigger_stop(self):
        self.__trigger_stop.set()
