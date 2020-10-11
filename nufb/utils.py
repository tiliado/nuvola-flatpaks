# Copyright 2019-2020 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.
"""
This module contains various utility functions.
"""
import os
import shutil
from pathlib import Path
from typing import Union, Optional

import ruamel.yaml

from nufb.logging import get_logger

LOGGER = get_logger(__name__)
YAML_LOADER = ruamel.yaml.YAML(typ='safe')


def load_yaml(source: Union[str, Path]) -> dict:
    """
    Load YAML source file/string as Python dictionary.

    :param source: The source file or string.
    :return: Python representation of the YAML document.
    """
    dictionary = YAML_LOADER.load(source)
    assert isinstance(dictionary, dict)
    return dictionary


def get_user_cache_dir(subdir: Optional[str] = None) -> Path:
    """
    Get user's cache directory or its subdirectory.

    :param subdir: The subdirectory to get or None.
    :return: User's cache directory or its subdirectory.
    """
    xdg_cache_dir = os.environ.get('XDG_CACHE_HOME')
    if xdg_cache_dir:
        cache_dir = Path(xdg_cache_dir).resolve()
    else:
        cache_dir = Path.home() / '.cache'
    return cache_dir / subdir if subdir else cache_dir


def hardlink_or_copy(source: Path, destination: Path) -> bool:
    """
    Hardlink the source to the destination or make a copy if hardlink fails.

    :param source: The source file.
    :param destination: The destination file.
    :return: `True` if file was hard-linked `False` if it was copied
    :raise OSError: On failure.
    """
    try:
        os.link(source, destination)
        LOGGER.debug("File %r linked to %r.", source, destination)
        return True
    except OSError as e:
        # Invalid cross-device link
        if e.errno != 18:
            raise
        shutil.copy2(source, destination)
        LOGGER.warning("File %r copied to %r.", source, destination)
        return False


def get_data_path(path: Optional[str] = None) -> Path:
    data_dir = Path(__file__).parent / "data"
    return data_dir / path if path else data_dir
