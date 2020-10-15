# Copyright 2019-2020 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.
"""
This module contains various utility functions.
"""
import asyncio
import os
import re
from asyncio.subprocess import DEVNULL, PIPE, STDOUT
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, cast

import aiofiles
import aiofiles.os
import ruamel.yaml

from nufb import fs
from nufb.logging import get_logger

LOGGER = get_logger(__name__)
YAML_LOADER = ruamel.yaml.YAML(typ="safe")
SUBST_RE = re.compile(r"@(\w+)@")


async def load_yaml(source: Union[str, Path], subst: Dict[str, Any] = None) -> dict:
    """
    Load YAML source file/string as Python dictionary.

    :param subst: Substitutions.
    :param source: The source file or string.
    :return: Python representation of the YAML document.
    """
    async with aiofiles.open(source) as fh:
        data = await fh.read()

    if subst is not None:
        data = SUBST_RE.sub(lambda m: cast(Dict[str, str], subst)[m.group(1)], data)

    dictionary = YAML_LOADER.load(StringIO(data))
    assert isinstance(dictionary, dict)
    return dictionary


def get_user_cache_dir(subdir: Optional[str] = None) -> Path:
    """
    Get user's cache directory or its subdirectory.

    :param subdir: The subdirectory to get or None.
    :return: User's cache directory or its subdirectory.
    """
    xdg_cache_dir = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache_dir:
        cache_dir = Path(xdg_cache_dir).resolve()
    else:
        cache_dir = Path.home() / ".cache"
    return cache_dir / subdir if subdir else cache_dir


async def hardlink_or_copy(source: Path, destination: Path) -> bool:
    """
    Hardlink the source to the destination or make a copy if hardlink fails.

    :param source: The source file.
    :param destination: The destination file.
    :return: `True` if file was hard-linked `False` if it was copied
    :raise OSError: On failure.
    """
    try:
        await fs.hardlink(source, destination)
        LOGGER.debug("File %r linked to %r.", source, destination)
        return True
    except OSError as e:
        # Invalid cross-device link
        if e.errno != 18:
            raise
        await fs.copy(source, destination)
        LOGGER.warning("File %r copied to %r.", source, destination)
        return False


def get_data_path(path: Optional[str] = None) -> Path:
    data_dir = Path(__file__).parent / "data"
    return data_dir / path if path else data_dir


async def exec_subprocess(argv, *, stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, **kwargs) -> Tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(*argv, stdin=stdin, stdout=stdout, stderr=stderr, **kwargs)
    stdout, stderr = await proc.communicate()
    assert not stderr
    result = await proc.wait()
    return result, stdout.decode("utf-8")
