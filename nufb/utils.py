# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""
This module contains various utility functions.
"""
from pathlib import Path
from typing import MutableMapping, Any, Union, Optional, TypeVar, Type

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
