"""
This module contains various utility functions.
"""

from typing import MutableMapping, Any


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
