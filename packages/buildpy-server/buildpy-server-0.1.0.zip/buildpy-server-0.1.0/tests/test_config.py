# -*- coding: utf-8 -*-

from pluggy import PluginManager
import buildpy_server.log


def test_get_pluginmanager(pluginmanager):
    """Make sure we can get a pluginmananger"""
    assert isinstance(pluginmanager, PluginManager)

    
def test_get_pluginmanager_name(pluginmanager):
    """Make sure the pluginmananger has the correct name."""
    assert pluginmanager.project_name == 'buildpy-server'


def test_add_hookspec(pluginmanager):
    """Make sure hooks get registered."""
    pmdict = pluginmanager.hook.__dict__
    assert 'buildpyserver_add_parser_options' in pmdict
