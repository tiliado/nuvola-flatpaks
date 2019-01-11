# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Tests for nufb.utils"""
from pathlib import Path

import pytest

from nufb import utils

KEY = 'key'
DEFAULT = 'default'


class TestExpectType:
    """Tests for nufb.utils.expect_type"""

    def test_none(self):
        """None raises TypeError"""
        with pytest.raises(
                TypeError,
                match=r'.+int.+expected but .+NoneType.+provided.*'):
            utils.expect_type(None, int)

    def test_wrong_type(self):
        """Wrong type raises TypeError"""
        with pytest.raises(
                TypeError,
                match=r'.+int.+expected but .+str.+provided.*'):
            utils.expect_type('abc', int)

    def test_correct_type(self):
        """Correct type returns the value itself"""
        value = 'abc'
        result = utils.expect_type(value, str)
        assert id(value) == id(result)


class TestEnsureList:
    """Tests for nufb.utils.ensure_list."""

    def test_missing_key(self):
        """New empty list is created, set, and returned for missing key."""
        dictionary = {}
        result = utils.ensure_list(dictionary, KEY)
        assert result == []
        assert id(dictionary[KEY]) == id(result)
        assert id(utils.ensure_list(dictionary, KEY)) == id(result)

    def test_empty_list(self):
        """Already existing empty list is returned unmodified."""
        empty = []
        dictionary = {KEY: empty}
        result = utils.ensure_list(dictionary, KEY)
        assert id(result) == id(empty)
        assert result == []
        assert id(utils.ensure_list(dictionary, KEY)) == id(empty)

    def test_non_empty_list(self):
        """Already existing non-empty list is returned unmodified."""
        not_empty = ['value']
        dictionary = {KEY: not_empty}
        result = utils.ensure_list(dictionary, KEY)
        assert id(result) == id(not_empty)
        assert result == ['value']
        assert id(utils.ensure_list(dictionary, KEY)) == id(not_empty)

    def test_wrong_type(self):
        """If the value is not a list, TypeError is raised."""
        dictionary = {KEY: 'value'}
        with pytest.raises(TypeError):
            utils.ensure_list(dictionary, KEY)


class TestEnsureString:
    """Tests for nufb.utils.ensure_string."""

    def test_missing_key_without_default(self):
        """KeyError is thrown for missing key without a default value."""
        dictionary = {}
        with pytest.raises(TypeError):
            utils.ensure_string(dictionary, KEY)
        assert KEY not in dictionary

    def test_missing_key_with_default(self):
        """A default value is set and returned for missing key."""
        dictionary = {}
        result = utils.ensure_string(dictionary, KEY, DEFAULT)
        assert id(dictionary[KEY]) == id(result) == id(DEFAULT)
        assert id(utils.ensure_string(dictionary, KEY)) == id(result)

    def test_empty_string(self):
        """Already existing empty string is returned unmodified."""
        empty = ''
        dictionary = {KEY: empty}
        result = utils.ensure_string(dictionary, KEY, DEFAULT)
        assert id(result) == id(empty)
        assert id(utils.ensure_string(dictionary, KEY)) == id(empty)

    def test_non_empty_string(self):
        """Already existing non-empty string is returned unmodified."""
        not_empty = 'value'
        dictionary = {KEY: not_empty}
        result = utils.ensure_string(dictionary, KEY, DEFAULT)
        assert id(result) == id(not_empty)
        assert result == 'value'
        assert id(utils.ensure_string(dictionary, KEY)) == id(not_empty)

    def test_wrong_type(self):
        """If the value is not a string, TypeError is raised."""
        dictionary = {KEY: ['value']}
        with pytest.raises(TypeError):
            utils.ensure_string(dictionary, KEY)


class TestLoadYaml:
    """Rests for nufb.utils.load_yaml."""

    def test_load_string(self):
        """Load YAML from string."""
        result = utils.load_yaml('a: b\nb: c\n')
        assert result == {'a': 'b', 'b': 'c'}

    def test_load_file(self, data_dir: Path):
        """Load YAML from string."""
        path = data_dir / 'document.yaml'
        result = utils.load_yaml(path)
        assert result == {'a': 'b', 'b': 'c'}
