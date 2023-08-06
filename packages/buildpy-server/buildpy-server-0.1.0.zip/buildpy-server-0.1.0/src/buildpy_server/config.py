# -*- coding: utf-8 -*-

from pluggy import PluginManager
from buildpy_server import log
from buildpy_server.BuildpyArgumentParser import BuildpyArgumentParser
from . import parseroptions
from . import hookspecs

logger = log.get_logger(__name__)


def get_pluginmanager():
    """Create Plugin manager, register hooks, load plugins with entry
    points named `buildpyserver`and return it.

    :returns: The PluginManager for buildpy-server
    :rtype: `PluginManager`
    """

    logger.info("Registering Pluginmanager")
    pm = PluginManager('buildpy-server')

    logger.info("Adding hook specifications")
    pm.add_hookspecs(hookspecs)

    logger.info("Loading entry points and registering plugins")
    pm.load_setuptools_entrypoints("buildpy_server")
    pm.register(parseroptions)
    logger.debug("Loaded plugins: %s" % pm.list_name_plugin())

    
    pm.check_pending()
    return pm


def try_argcomplete(parser):
    """Make sure to use argcomplete if it is installed.

    :param parser: the parser to add autocomplete
    """

    try:
        import argcomplete
    except ImportError:
        pass
    else:
        argcomplete.autocomplete(parser)

        
def get_parser():
    logger.info("Getting ArgumentParser")
    return BuildpyArgumentParser(description="Run a build.")
   

def parse_options(pluginmanager, parser, argv):
    """Build a parser and call all add options hooks.

    :param pluginmanager: The Buildpy default pluginmanager.
    :param argv: all commandline arguments
    :returns: a configuration object containing all parsed arguments
    """
    
    logger.info("Calling \"add parser options\" hooks")
    logger.debug("Designated hook callers: %s"
                 % pluginmanager._plugin2hookcallers.keys())
    pluginmanager.hook.buildpyserver_add_parser_options(
        parser=parser)

    try_argcomplete(parser)
    raw = [str(x) for x in argv[1:]]

    logger.info("Parsing arguments to namespace")
    args = parser.parse_args(raw)
    args._raw = raw

    logger.info("Creating global configuration object")
    config = Config(args, pluginmanager, parser)
    return config


class Config(object):
    """Buildpy's configuration object enables access to different
    configurations and values.
    """
    
    def __init__(self, args, pluginmanager, parser):
        """Initialize a configuration.
        
        :param args: Arguments as a parsed namespace.
        :param pluginmanager: The registered pluginmananger.
        :param parser: The parser used to parse command line.
        """

        self.args = args
        self.pm = pluginmanager
        self.parser = parser
