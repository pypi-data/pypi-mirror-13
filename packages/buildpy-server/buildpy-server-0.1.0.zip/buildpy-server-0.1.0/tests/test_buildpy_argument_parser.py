# -*- coding: utf-8 -*-

from buildpy_server.BuildpyArgumentParser import BuildpyArgumentParser
import buildpy_server.log
from argparse import _ArgumentGroup


logger = buildpy_server.log.get_logger(__name__)


def test_buildpy_argument_parser():
    """Instanciate a buildpy argument parser."""

    parser = BuildpyArgumentParser(description="Buildpy Parser")
    assert isinstance(parser, BuildpyArgumentParser)
    assert parser.description == "Buildpy Parser"


def test_add_option(buildpy_argument_parser):
    """Add an option the the parser."""

    buildpy_argument_parser.add_option("--hello", type=str)
    args = buildpy_argument_parser.parse_args(["--hello", "world"])
    assert args.hello == "world"


def test_add_group(buildpy_argument_parser):
    """Create a group and add one option to the argument parser."""

    grp_title = "hellogrp"
    grp = buildpy_argument_parser.add_group(grp_title)
    assert isinstance(grp, _ArgumentGroup)
    assert grp.title == grp_title

    # add option to grp
    opt_title = "--hello"
    grp.add_option(opt_title, type=str)
    buildpy_argument_parser.parse_args([opt_title, "world"])
    assert "--hello" in grp._option_string_actions
