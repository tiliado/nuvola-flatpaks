"""Tests for nufb.utils"""
from pathlib import Path

import pytest

from nufb import utils


class TestEnsureList:
    """Tests for nufb.utils.ensure_list."""

    def test_missing_key(self):
        """New empty list is created, set, and returned for missing key."""
        dictionary = {}
        result = utils.ensure_list(dictionary, 'name')
        assert result == []
        assert id(dictionary['name']) == id(result)
        assert id(utils.ensure_list(dictionary, 'name')) == id(result)

    def test_empty_list(self):
        """Already existing empty list is returned unmodified."""
        empty = []
        dictionary = {'name': empty}
        result = utils.ensure_list(dictionary, 'name')
        assert id(result) == id(empty)
        assert result == []
        assert id(utils.ensure_list(dictionary, 'name')) == id(empty)

    def test_non_empty_list(self):
        """Already existing non-empty list is returned unmodified."""
        not_empty = ['value']
        dictionary = {'name': not_empty}
        result = utils.ensure_list(dictionary, 'name')
        assert id(result) == id(not_empty)
        assert result == ['value']
        assert id(utils.ensure_list(dictionary, 'name')) == id(not_empty)

    def test_type_error(self):
        """If the value is not a list, TypeError is raised."""
        dictionary = {'name': 'value'}
        with pytest.raises(TypeError):
            utils.ensure_list(dictionary, 'name')


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
