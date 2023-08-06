# -*- coding: utf-8 -*-

import pluggy

hookspec = pluggy.HookspecMarker("buildpy-server")


@hookspec
def buildpyserver_add_parser_options(parser):
    """Allows to add commandline options and is called before the
    actual parsing.
    """


@hookspec
def buildpyserver_manipulate_path(config):
    """Allows manipulation of environments. This is handy to setup
    a specific shell environment or to change `PATH`.
    Hook `run_test_commands` does recognize a changed environment.
    """


@hookspec
def buildpyserver_run_test_commands(config):
    """Allows to run arbitary commands which are defined in the
    test section of the config file.
    Depending on what the commands are, this can be dangerous. It
    should be clear, that whatever you define in test section is
    run without further safety measures."""


@hookspec
def buildpyserver_on_success(config):
    """Hook called whenever all testcommands 
    finish successfully."""


@hookspec
def buildpyserver_on_failure(config):
    """Hook called whenever at least one testcommand failed."""
