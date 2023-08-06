# -*- coding: utf-8 -*-

from buildpy_server import main
import buildpy_server
import sys


def test_version(capfd, buildpy_args):
    """Test if buildpy-server can outout its own version."""
    main.main(buildpy_args)
    out, err = capfd.readouterr()
    assert not err
    assert buildpy_server.__version__ in out.strip()


def test_early_out(mocker):
    """When supplying no arguments, early out."""
    mocker.patch("sys.exit", autospec=True)
    main.main(['buildpy-server'])
    sys.exit.assert_called_once_with(1)


def test_early_out_with_unknown_args(mocker):
    """When supplying unrecognized arguments, raise error and call
    sys.exit(2)."""
    
    mocker.patch("sys.exit", autospec=True)
    main.main(['buildpy-server', '\\\\\\n'])
    sys.exit.assert_called_once_with(2)


def test_call_hooks_from_main(mocker, buildpy_args):
    """Test whether calling ` _call_hooks` from `main` works
    and is only called once."""
    
    mocker.patch("buildpy_server.main._call_hooks", autospec=True)
    mocker.patch("buildpy_server.config.Config")
    config = buildpy_server.config.Config()
    main.main(buildpy_args)
    buildpy_server.main._call_hooks.assert_called_once_with(config)


def test_call_hooks(mocker):
    """Test calling `_call_hooks` directly to assure specific
    run path (if rc == True)."""
    
    mocker.patch("buildpy_server.config.Config")
    mocker.patch("buildpy_server.main.logger.info", autospec=True)
    config = buildpy_server.config.Config()
    config.rc = 1
    main._call_hooks(config)
    buildpy_server.main.logger.info.assert_called_once_with(
        "A test command failed")
