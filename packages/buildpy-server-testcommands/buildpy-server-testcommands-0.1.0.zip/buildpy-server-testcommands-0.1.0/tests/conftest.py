# -*- coding: utf-8 -*-

import pytest
from buildpy_server.BuildpyArgumentParser import BuildpyArgumentParser


@pytest.fixture()
def buildpy_argument_parser():
    """Fixture to get a fresh `BuildpyArgumentParser`"""
    return BuildpyArgumentParser()
