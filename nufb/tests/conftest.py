# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Fixtures for pytest"""

from pathlib import Path

import pytest

from nufb.wrappers import Manifest


@pytest.fixture
def data_dir() -> Path:
    """
    Get data dir of tests.

    :return: The data dir of tests.
    """
    return Path(__file__).parent / 'data'


@pytest.fixture
def manifest() -> Manifest:
    """Create a simple valid manifest."""
    return Manifest({'id': 'eu.tiliado.Test'})
