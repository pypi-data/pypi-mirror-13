# -*- coding: utf-8 -*-

from . import log
from .config import get_pluginmanager, get_parser, parse_options
from . import __version__ as buildpy_server_version
import sys

# instantiate a preconfigured logger
logger = log.get_logger(__name__)


def main(argv=sys.argv):
    logger.debug("CLI arguments: %s" % argv)

    # get plugin manager and try to run configuration
    return _main(get_pluginmanager(), get_parser(), argv)


def _main(pluginmanager, parser, argv):    
    config = parse_options(pluginmanager, parser, argv)
    
    # early out if no arguments are given    
    if len(argv) == 1:
        config.parser.print_help()
        sys.exit(1)
        
    logger.debug(config.args)      

    if config.args.version:
        print(buildpy_server_version)

    _call_hooks(config)
    

def _call_hooks(config):
    # manipulate path hooks
    config.env = config.pm.hook.buildpyserver_manipulate_path(
        config=config)

    logger.debug("config environments are: %s" %config.env)
    # test command hooks
    config.rc = config.pm.hook.buildpyserver_run_test_commands(
        config=config)

    # on failure and on success hooks
    if any(config.rc) == True:
        logger.info("A test command failed")
        config.pm.hook.buildpyserver_on_failure(config=config)
    else:
        config.pm.hook.buildpyserver_on_success(config=config)
