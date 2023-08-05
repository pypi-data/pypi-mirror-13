"""
Defines configuration settings and facilitates XML loading & saving.
"""
#import os
import importlib
try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict
from . import constraints, settings

#def str2bool(val):
#    return val.lower() == 'true'
#
#
#str_empty_if_none = lambda val: val if val is not None else ''

#
# Defines configuration settings to XML element names and value validators, so they can be saved/loaded from an external file.
# Members are four-tuples of (setting name, default value, validator function).
#

CONFIG_SETTINGS = (
    ('CORALOGIX_API_ENDPOINT', 'https://test.coralogix.com/sdk/v1', None),
    ('IS_ACTIVE', True, None),
    ('IS_PRODUCTION_MODE', True, None),
    ('APPLICATION_NAME', '', None),
    ('SUBSYSTEM_NAME', '', None),

    # Validatable settings
    ('BULK_TIME_IN_MILLI_THRESHOLD', 1000,
        lambda val: constraints.MIN_BULK_TIME_IN_MILLI_THRESHOLD <= val <= constraints.MAX_BULK_TIME_IN_MILLI_THRESHOLD),
    ('BULK_SIZE_IN_KIB_THRESHOLD', 500,
        lambda val: constraints.MIN_BULK_SIZE_IN_KIB_THRESHOLD <= val <= constraints.MAX_BULK_SIZE_IN_KIB_THRESHOLD),
    ('BUFFER_MAX_SIZE_IN_KIB', 4000,
        lambda val: constraints.MIN_BUFFER_MAX_SIZE_IN_KIB <= val <= constraints.MAX_BUFFER_MAX_SIZE_IN_KIB),
    ('AUTHENTICATION_RETRIES', 3,
        lambda val: constraints.MIN_AUTHENTICATION_RETRIES <= val <= constraints.MAX_AUTHENTICATION_RETRIES),
    ('FLUSH_RETRIES', 3,
        lambda val: constraints.MIN_FLUSH_RETRIES <= val <= constraints.MAX_FLUSH_RETRIES),
    ('PERCENTAGE_OF_BUFFER_NORMAL_COMPLETENESS', 50,
        lambda val: constraints.MIN_PERCENTAGE_OF_BUFFER_NORMAL_COMPLETENESS <= val <= constraints.MAX_PERCENTAGE_OF_BUFFER_NORMAL_COMPLETENESS),
    ('INTERVAL_IN_MILLI_FOR_TIMER_ON_DISCONNECTION', 5000,
        lambda val: constraints.MIN_INTERVAL_IN_MILLI_FOR_TIMER_ON_DISCONNECTION <= val <= constraints.MAX_INTERVAL_IN_MILLI_FOR_TIMER_ON_DISCONNECTION),
    ('LOG_PERFORMANCE_DATA_INTERVAL', 30000,
        lambda val: constraints.MIN_LOG_PERFORMANCE_DATA_INTERVAL <= val <= constraints.MAX_LOG_PERFORMANCE_DATA_INTERVAL),
    ('RELOAD_CONFIG_INTERVAL', 120000,
        lambda val: constraints.MIN_RELOAD_CONFIG_INTERVAL <= val <= constraints.MAX_RELOAD_CONFIG_INTERVAL),
    ('INTERVAL_IN_MILLI_TO_FLUSH_LOCAL_LOG', 5000,
        lambda val: constraints.MIN_INTERVAL_IN_MILLI_TO_FLUSH_LOCAL_LOG <= val <= constraints.MAX_INTERVAL_IN_MILLI_TO_FLUSH_LOCAL_LOG),
    ('INTERVAL_IN_MILLI_TO_SLEEP_BETWEEN_RETRIES', 200,
        lambda val: constraints.MIN_INTERVAL_IN_MILLI_TO_SLEEP_BETWEEN_RETRIES <= val <= constraints.MAX_INTERVAL_IN_MILLI_TO_SLEEP_BETWEEN_RETRIES),
    ('INTERVAL_IN_MILLI_TO_START_TRYING_TO_RECONNECT', 2000,
        lambda val: constraints.MIN_INTERVAL_IN_MILLI_TO_START_TRYING_TO_RECONNECT <= val <= constraints.MAX_INTERVAL_IN_MILLI_TO_START_TRYING_TO_RECONNECT),
    ('TIMEOUT_IN_MILLI_FOR_REQUESTS', 5000,
        lambda val: constraints.MIN_TIMEOUT_IN_MILLI_FOR_REQUESTS <= val <= constraints.MAX_TIMEOUT_IN_MILLI_FOR_REQUESTS),
    ('INNER_LOG_FILE_MAX_SIZE_IN_KIB', 2000,
        lambda val: constraints.MIN_INNER_LOG_FILE_MAX_SIZE_IN_KIB <= val <= constraints.MAX_INNER_LOG_FILE_MAX_SIZE_IN_KIB),
    ('INTERVAL_IN_MILLI_TO_SYNC_CORALOGIX_TIME', 30000,
        lambda val: constraints.MIN_INTERAL_IN_MILLI_TO_SYNC_CORALOGIX_TIME <= val <= constraints.MAX_INTERAL_IN_MILLI_TO_SYNC_CORALOGIX_TIME)
)

def reload_settings():
    ''' Reloads the settings.py file using python's importlib.
        This function does not change CORALOGIX_API_ENDPOINT. '''
    api_endpoint = settings.CORALOGIX_API_ENDPOINT
    importlib.reload(settings)
    settings.CORALOGIX_API_ENDPOINT = api_endpoint

def as_dict():
    "Returns all settings in an OrderedDict instance. Items are ordered as they are defined in CONFIG_SETTINGS."
    result = OrderedDict()
    for setting in CONFIG_SETTINGS:
        result[setting[0]] = getattr(settings, setting[0])
    return result


### Initialization ###
def load_settings(dir_path):
    for setting in CONFIG_SETTINGS:
        val = getattr(settings, setting[0])
        if ((setting[2] is not None) and # If there is a validator function, and
            (not setting[2](val))): # the value is invalid:
            #TODO: add logger() call to file/whatever to report invalid value
            setattr(settings, setting[0], setting[1]) # and set the default
    #        raise ValueError(setting[0])
