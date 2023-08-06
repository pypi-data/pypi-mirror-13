# -*- coding: utf-8 -*-

from buildpy_server import log
import logging

logger = log.get_logger(__name__, level=logging.DEBUG)


def test_buildpy_logger():
    assert isinstance(logger, logging.Logger)
