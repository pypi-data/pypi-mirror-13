# -*- coding: utf-8 -*-

import pytest
from buildpy_server import config
from buildpy_server.BuildpyArgumentParser import BuildpyArgumentParser


@pytest.fixture
def pluginmanager():
    """Fixture to get a fresh `PluginManager`"""
    return(config.get_pluginmanager())


@pytest.fixture()
def buildpy_argument_parser():
    """Fixture to get a fresh `BuildpyArgumentParser`"""
    return BuildpyArgumentParser()


@pytest.fixture()
def buildpy_args():
    return ['buildpy-server', '--version']
