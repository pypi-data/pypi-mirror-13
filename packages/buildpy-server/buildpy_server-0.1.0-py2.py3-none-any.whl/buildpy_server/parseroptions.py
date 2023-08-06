# -*- coding: utf-8 -*-

import pluggy
import buildpy_server
import argparse
from . import log

logger = log.get_logger(__name__)

hookimpl = pluggy.HookimplMarker('buildpy-server')


@hookimpl
def buildpyserver_add_parser_options(parser):
    build = parser.add_group("build options")
    build.add_option("--version", action="store_true",
                     help="show buildpy version (%s)"
                     % buildpy_server.__version__)
