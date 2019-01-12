# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""
This module contains various utility functions.
"""
import os
import shutil
from pathlib import Path
from typing import MutableMapping, Any, Union, Optional, TypeVar, Type, List

import ruamel.yaml

T = TypeVar('T')


def expect_type(value: Any, typ: Type[T]) -> T:
    """
    Check that the value has a correct type.

    :param value: The value.
    :param typ: The expected type.
    :return: The value if the tpe is correct.
    :raise TypeError: If the types differ.
    """
    if not isinstance(value, typ):
        raise TypeError(f'{typ} expected but {type(value)} provided.')
    return value


def ensure_list(dictionary: MutableMapping[Any, Any], key: str) -> list:
    """
    Ensure that a mutable mapping contains a list for the specified key.

    If there is no value for the key, a new empty list is set and then
    returned. If the value is a list, it is returned unchanged. Otherwise,
    TypeError is raised.

    :param dictionary: The mutable mapping.
    :param key: The key that should contain a list.
    :return: The list for the given key.
    :raise TypeError: If the value for the given key is not a list.
    """
    try:
        array = dictionary[key]
        if isinstance(array, list):
            return array
        raise TypeError(
            f'The value for key {key!r} is not a list but {type(array)}.')
    except KeyError:
        new_array: list = []
        dictionary[key] = new_array
        return new_array


def ensure_string(dictionary: MutableMapping[Any, Any], key: str,
                  default: Optional[str] = None) -> str:
    """
    Ensure that a mutable mapping contains a string value for the specified
    key.

    If the existing value for the key is a string, it is returned. If there is
    no value for the key and `default` is not `None`, it is set as the new
    value for the key and then returned. Otherwise, an exception is raised.

    :param dictionary: The mutable mapping.
    :param key: The key that should contain a string value.
    :param default: The value to use if there is no value for the given key.
    :return: The list for the given key.
    :raise TypeError: If the existing value for the given key is not a
        string, or if there is no existing value for the given key and
        `default` is `None`.
    """
    try:
        value = dictionary[key]
        if isinstance(value, str):
            return value
        raise TypeError(
            f'The value for key {key!r} is not a string but {type(value)}.')
    except KeyError:
        if default is None:
            raise TypeError(
                f'The value for key {key!r} is missing and no default value '
                'was provided.')
        dictionary[key] = default
        return default


def load_yaml(source: Union[str, Path]) -> dict:
    """
    Load YAML source file/string as Python dictionary.

    :param source: The source file or string.
    :return: Python representation of the YAML document.
    """
    yaml = ruamel.yaml.YAML(typ='safe')
    dictionary = yaml.load(source)
    assert isinstance(dictionary, dict)
    return dictionary


def add_unique(lst: List[T], value: T) -> bool:
    """
    Adds a value to a list but only if not already present.

    If you don't need to have the items ordered and the items are hashable,
    consider using :meth:`set.add` of Python's built-in :class:`set`
    data type instead as it provides better performance.

    :param lst: The list to add the value to.
    :param value: The value to add to the list.
    :return: `True` if the value was added to the list, `False` otherwise.
    """
    if value in lst:
        return False
    lst.append(value)
    return True


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
        os.link(str(source), str(destination))
        return True
    except OSError as e:
        # Invalid cross-device link
        if e.errno != 18:
            raise
        shutil.copy2(str(source), str(destination))
        return False
