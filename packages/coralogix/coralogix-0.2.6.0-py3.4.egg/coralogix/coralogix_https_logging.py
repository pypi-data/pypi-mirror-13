
import sys
import time
import json
import signal
import logging
import threading
from socket import getfqdn
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


class CoralogixHandlerTasks(object):
    
    class CoralogixHandlerTask(object):
        def __init__(self, task_name, function, trigger_interval):
            self.task_name = task_name  # Name of the task
            self.function = function  # Function object which runs the task
            self.trigger_interval = trigger_interval  # Number of timebins between consecutive triggers of the task
            self.finished = True  # Flag for marking the task as completed; When =False, the task will not run
        def check_interval(self, timebins):
            """ Returns True if task should execute at the current timebin provided. """
            return timebins % self.trigger_interval == 0
        def run_by_interval(self, timebins, *args, **kwargs):
            """ Checks if the task should run by self.check_interval(), and runs the task with *args and **kwargs. """
            if self.check_interval(timebins):
                self.run(*args, **kwargs)
        def run(self, *args, **kwargs):
            """ Runs the task with *args and **kwargs, and self.untrigger() the task if asked by turn_off_trigger. """
            if self.finished:  # Prevents the task from re-executing before it finishes
                self.finished = False
                self.function(*args, **kwargs)
                self.finished = True
        
    def __init__(self):
        self.tasks = dict()  # { task_name : CoralogixHandlerTask }
        self.task_names = list()  # An ordered list of task_names
    def add_task(self, task_name, function, trigger_interval):
        task = self.CoralogixHandlerTask(task_name, function, trigger_interval)
        self.tasks[task_name] = task
        self.task_names.append(task_name)
    def remove_task(self, task_name):
        task = self.tasks.get(task_name)
        if task:
            del self.tasks[task_name]
            self.task_names.remove(task_name)
    def get_task_order(self):
        return self.task_names
    def get_task(self, task_name):
        return self.tasks.get(task_name)


class CoralogixHTTPSHandler(Handler, object):
    
    # Server timedelta parameters:
    _get_time_url = "https://api.coralogix.com/sdk/v1/time"  # URL to get server timedelta
    # POST command parameters:
    _post_url = "https://api.coralogix.com/api/v1/logs"  # Coralogix URL for http-post requests
    _post_headers = {"Content-Type": "application/json"}
    _post_timeout = 5  # Timeout in seconds for http-post requests
    _post_max_log_entries = 2000  # Maximum log entries inside each bulk POST command
    
    # Trigger tasks parameters:
    _timebin_base_unit = 1  # Size of the basic timebin in seconds; multiplications of this unit are used to trigger events.
    _send_logs_interval = 5  # Trigger send logs every (5) timebin_base_units
    _check_log_buffer_interval = 1  # Trigger checking log buffer every (1) timebin_base_units
    _update_server_timedelta_interval = 600  # Trigger updating timedelta from server every (600) timebin_base_units
    
    # _post_time_interval = 5  # Time interval in seconds for triggering a POST command
    _log_count_trigger = 1000  # Min log count in queue for triggering a POST command
    # _check_count_time_interval = 1  # Time interval between consecutive log count checks

    def __init__(self, company_id, private_key, application, subsystem, computer_name=None, post_url=None, silence_exceptions=True):
        """
        If silence_exceptions is True, exceptions will be silenced when encountered.
        :param company_id: int; integer representing the company_id
        :param private_key: str; company private key UUID
        :param application: str; name of the application the logger belongs to
        :param subsystem: str; name of the subsystem the logger belongs to
        :param computer_name: str; computer name the logger runs from; automatically retrieved from socket.getfqdn() if None
        :param post_url: str; override the default send_logs URL
        :param silence_exceptions: bool; flag for silencing internal exceptions
        """
        super(CoralogixHTTPSHandler, self).__init__()
        self._exception_formatter = logging.Formatter().formatException
        self._post_url = post_url or self._post_url
        # Exceptions handling:
        self.silence_exceptions = silence_exceptions
        # Coralogix Parameters:
        self.company_id = company_id
        self.private_key = private_key
        self.application = application
        self.subsystem = subsystem
        self.computer_name = computer_name or getfqdn()  # If computer_name is not provided, retrieve fully-qualified domain name
        # Log variables:
        self._queue = Queue()
        self._received_logs_counter = 0
        self._sent_logs_counter = 0
        self._server_timedelta = 0  # Timedelta in milliseconds to add to logs for server sync
        
        # Event triggers:
        self.__trigger_update_timedelta = threading.Event()  # Event for triggering update_timedelta
        self.__trigger_send = threading.Event()  # Event for triggering send_logs
        self.__trigger_stop = threading.Event()  # Event for gracefully stopping the handler
        # Activate send_logs() thread -- runs on a different thread as it requires HTTP post:
        self.send_logs_thread = threading.Thread(target=self.send_logs)
        self.send_logs_thread.daemon = True  # Prevents the thread from closing before the buffer is empty
        self.send_logs_thread.start()
        signal.signal(signal.SIGINT, self.close)  # Attach signal handlers for graceful exit
        signal.signal(signal.SIGTERM, self.close)  # Attach signal handlers for graceful exit
        # Activate get_server_timedelta() thread  -- runs on a different thread as it requires HTTP post:
        self.get_server_timedelta_thread = threading.Thread(target=self.get_server_timedelta)
        self.get_server_timedelta_thread.daemon = True
        self.get_server_timedelta_thread.start()
        # Construct task checker:
        self._time_bins_counter = 0  # Counter for number of timebin intervals used to execute tasks
        self.handler_tasks = CoralogixHandlerTasks()
        # Task definitions; for tasks which require outside sources, e.g. HTTP post, the
        # task executed should be a threading.Event() trigger. This way these will
        # run async and will not freeze the rest of the tasks. "send_logs" and
        # "update_server_timedelta" are such tasks.
        # tasks are executed according to their order in the list:
        handler_tasks = [("update_server_timedelta", self.__trigger_update_timedelta.set, self._update_server_timedelta_interval),
                         ("check_log_buffer", self.trigger_by_log_num, self._check_log_buffer_interval),
                         ("send_logs", self._trigger_send, self._send_logs_interval)]
        for task in handler_tasks:
            self.handler_tasks.add_task(*task)
        self.handler_tasks.get_task("update_server_timedelta").run()  # Run the update_server_timedelta task immediately
        self.__trigger_tasks = DaemonTimer(self._timebin_base_unit, self.trigger_tasks)
        self.__trigger_tasks.daemon = True
        self.__trigger_tasks.start()
        
    def trigger_tasks(self):
        start_time = time.time()
        self.__trigger_tasks.cancel()
        self._time_bins_counter += 1  # Increase the time_bins counter
        # Iterate through the tasks and execute if needed (timebins passed and last execution finished):
        for task_name in self.handler_tasks.get_task_order():
            self.handler_tasks.get_task(task_name).run_by_interval(self._time_bins_counter)
        execution_time = time.time() - start_time
        new_timer_time = max(0, self._timebin_base_unit-execution_time)
        if not self._stopped():
            self.__trigger_tasks = DaemonTimer(new_timer_time, self.trigger_tasks)
            self.__trigger_tasks.daemon = True
            self.__trigger_tasks.start()
        else:
            del self.__trigger_tasks
        
    def emit(self, record):
        try:
            # Format the message:
            log_entry = dict()
            timestamp = record.__dict__.get("override_timestamp") or record.created
            log_entry["timestamp"] = timestamp * 1e3 + self._server_timedelta
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
            # Insert to queue and count the log recrod:
            self._queue.put_nowait(log_entry)
            self._received_logs_counter += 1
        except Exception:
            self.handleError(record)
        
    def send_logs(self):
        while not (self._stopped() and self._queue.empty()):
            self.__trigger_send.wait()
            self.__trigger_send.clear()
            # Send logs:
            try:
                if not self._queue.empty():
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
                    while not self._queue.empty() and log_entries_count < self._post_max_log_entries:
                        try:
                            log_message = self._queue.get_nowait()
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
                            self._sent_logs_counter += log_entries_count
            except Exception as e:
                if self.silence_exceptions is False:
                    raise
            # Create new timers and start them:
            if self.trigger_by_log_num_condition():  # Re-run the count test in case we had more than self._post_max_log_entries logs in the queue
                continue
        # Stop command executed, clearing and deleting the threading.Event:
        self.__trigger_send.clear()
        del self.__trigger_send

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
        """ Updates self._server_timedelta """
        while not self._stopped():
            self.__trigger_update_timedelta.wait()  # Wait for event to trigger,
            self.__trigger_update_timedelta.clear()  # cancel the event flag
            for i in range(3):  # and retry 3 times retrieve server timestamp:
                if self._stopped():
                    break  # break out of the loop if ordered to stop;
                try:
                    server_time = int(self.post(None, self._get_time_url).read()) / 1e4  # Server time in milliseconds
                    local_time = time.time() * 1e3  # Local time in milliseconds
                    if server_time:
                        self._server_timedelta = server_time - local_time
                        break
                except Exception:
                    continue
        # Stop command executed, clearing and deleting the threading.Event:
        self.__trigger_update_timedelta.clear()
        del self.__trigger_update_timedelta
        
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
    
    def trigger_by_log_num(self):  # Triggers a send logs event if enough logs are in the queue
        """ Triggers self.__trigger_send if number of logs exceeds self._log_count_trigger. """
        if self.trigger_by_log_num_condition():
            self._trigger_send()

    def trigger_by_log_num_condition(self):  # Returns True if enough logs are waiting in the queue
        return self._log_count_trigger <= self._queue.qsize()

    def flush(self):
        # Release any threading.Event() wait commands:
        self._trigger_send()
        self._trigger_update_timedelta()
    
    def close(self, frame=None, signal_code=None):
        # Hasten things by dropping http post timeout to 2 seconds:
        self._post_timeout = 2
        # Flush the buffer, trigger a stop event and wait for buffer clear:
        self.flush()
        self._trigger_stop()
        self.send_logs_thread.join()
    
    def _trigger_update_timedelta(self):  # Triggers an update timedelta event
        self.__trigger_update_timedelta.set()
        
    def _trigger_send(self):  # Triggers a send_logs event
        self.__trigger_send.set()

    def _trigger_stop(self):  # Triggers a stop event
        self.__trigger_stop.set()
        
    def _stopped(self):  # Returns True if the process has been ordered to sop
        return self.__trigger_stop.is_set()
