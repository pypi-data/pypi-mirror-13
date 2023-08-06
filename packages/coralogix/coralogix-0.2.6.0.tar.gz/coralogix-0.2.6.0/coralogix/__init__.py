"""
Coralogix SDK initialization module.
"""
#
# Constants
# 

VERSION = (0, 2, 6, 0)
get_version = lambda: '.'.join(str(x) for x in VERSION)
__version__ = get_version()
TICKS_IN_SECOND = 10**7
MICROSEC_IN_SEC = 10**6
CORALOGIX_ENCODING = 'utf-8'


#
# For Python 3: install correct SSL handler
#

try:
    from urllib import request
    import ssl
    if hasattr(ssl, 'SSLContext'):
        ssl_handler = request.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        ssl_opener = request.build_opener(ssl_handler)
        request.install_opener(ssl_opener)
except ImportError:
    pass


#
# Enumerations used throughout the SDK and in third-party applications.
#

try:
    from enum import Enum, IntEnum
except ImportError:
    from enum34 import Enum, IntEnum

# TODO: Make all values uppercase

class Category(Enum):
    (BusinessLogic,
    DataAccess,
    UILogic,
    UIComponents,
    Engine,
    System,
    Core,
    General,
    Configuration,
    Algorithm,
    Middleware,
    FrontEnd,
    BackEnd,
    SDK,
    API,
    Utilities,
    Database,
    Kernel,
    ClientSide,
    ServerSide,
    Infrastructure,
    Proxy) = range(22)


class Severity(IntEnum):
    Debug = 1
    Verbose = 2
    Info = 3
    Warning = 4
    Error = 5
    Critical = 6

#    def __str__(self):
#        return self.name


#
# Imports for use by third-party applications
# 

from .logger import CoralogixLogger
from coralogix.coralogix_logging import CoralogixHandler
from coralogix.coralogix_https_logging import CoralogixHTTPSHandler
