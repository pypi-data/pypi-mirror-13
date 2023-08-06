import logging
import sys

# Default log level defined for pickups
DEFAULT_LOGGING_LEVEL = logging.DEBUG
FORMAT = '%(asctime)s:%(module)s-%(lineno)d:%(levelname)s: %(message)s'


def setup_logger():
    """Setup pickups top-level logger with a StreamHandler
    Logger's root name is `buildpy-server`.
    """
    log = logging.getLogger("buildpy-server")
    log.propagate = False
    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = FORMAT
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    level = DEFAULT_LOGGING_LEVEL
    log.setLevel(level)


def get_logger(name, level=None):
    """This method returns a logger for the given name, configured using
    the above defined defaults.  One would use this in a module like::
    from pickups.log import get_logger log = get_logger(__name__)
    :param name: Name of the requested logger. Best is to stay with
    `__name__`. Buildpy-server's logger will append this to the root
    name.

    :param name: str
    :param level: one of :mod:`logging` levels (eg. DEBUG, INFO,
    CRITICAL, ...)
    :returns: A logger
    """
    log = logging.getLogger("buildpy-server.%s" % name)
    if level is not None:
        log.setLevel(level)
    return log


# setup the logger
setup_logger()
