"""
Exposes the CoralogixLogger functionality as a `logging.Handler` to be used by other Python modules.
"""
import logging
from coralogix import Severity
from .logger import CoralogixLogger

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


class CoralogixHandler(logging.Handler, object):
    "A logging handler class which sends logging records to the Coralogix service."
    def __init__(self, company_id, private_key, app_name=None, subsystem_name=None, config_dir=None):
        try:
            super(CoralogixHandler, self).__init__()
    
            self._coralogix_logger = CoralogixLogger(config_dir)
            self._coralogix_logger.connect(company_id, private_key, app_name, subsystem_name, raise_exceptions=False)
        except Exception as e:
            print("CoralogixHandler.__init__(): caught exception= {0} when connecting using company_id= {1}, private_key= {2}, app_name= {3}, subsystem_name= {4}".format(e, company_id, private_key, app_name, subsystem_name))

    def setFormatter(self, fmt):
        "Formatting is not needed for Coralogix."
        pass

    def emit(self, record):
        "Emits a record. Unlike Python's logging handlers, no formatting is needed for Coralogix."
        try:
            # No need to acquire the handler's IO lock, since CoralogixLogger locks on its own
            # try: # First try to find the exact severity
            #     level = LOGGING_LEVEL_MAP[record.levelno]
            # except KeyError: # If it does not exist, find nearest severity
            if record.levelno in LOGGING_LEVEL_MAP: # Switched to if/else to prevent the high cost of exception for a frequent operation.
                level = LOGGING_LEVEL_MAP[record.levelno]
            else:
                levels, levelno_key = sorted(LOGGING_LEVEL_MAP.keys()), None
                for i in range(len(levels) - 1):
                    if levels[i] < record.levelno < levels[i + 1]:
                        levelno_key = levels[i] if record.levelno - levels[i] <= abs(record.levelno - levels[i+1]) else levels[i+1]
                        break
                level = LOGGING_LEVEL_MAP[levelno_key]

            self._coralogix_logger.send_log(level, record.getMessage(), record.name, record.module, record.funcName)
        except Exception as e:
            self.handleError(record)
