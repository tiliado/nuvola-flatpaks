# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Tests for nufb.wrappers"""
import pytest

from nufb import wrappers


class TestManifest:
    """Tests for nufb.wrappers.Manifest"""

    def test_construct_no_data(self):
        """No need to provide data"""
        manifest = wrappers.Manifest()
        assert manifest.data == {}

    def test_construct_empty_data(self):
        """Empty data dictionary is ok"""
        data = {}
        manifest = wrappers.Manifest(data)
        assert manifest.data == {}
        assert id(manifest.data) == id(data)

    def test_id_field_present(self):
        """Recognize 'id' and 'app-id' field."""
        app_id = 'aaa'
        assert id(wrappers.Manifest({'id': app_id}).id) == id(app_id)
        assert id(wrappers.Manifest({'app-id': app_id}).id) == id(app_id)

    def test_duplicate_id_field(self):
        """No need to specify both 'id' and 'app-id'."""
        data = {'id': 'aaa', 'app-id': 'bbb'}
        with pytest.raises(ValueError):
            wrappers.Manifest(data)

    def test_id_field_missing(self):
        """Neither 'id' nor 'app-id' found."""
        data = {}
        with pytest.raises(TypeError):
            _ = wrappers.Manifest(data).id  # noqa

    def test_id_field_invalid(self):
        """Id field is a string."""
        data = {'id': 123}
        with pytest.raises(TypeError):
            _ = wrappers.Manifest(data).id  # noqa

    def test_set_id_field(self):
        """Test the setter."""
        data = {'app-id': 'old-id'}
        manifest = wrappers.Manifest(data)
        my_id = 'myid'
        manifest.id = my_id
        assert data['id'] == manifest.id == my_id
        assert 'app-id' not in data

        with pytest.raises(TypeError):
            manifest.id = 123
        assert data['id'] == manifest.id == my_id

    def test_branch_field_missing(self):
        """Neither 'id' nor 'app-id' found."""
        data = {}
        assert wrappers.Manifest(data).branch == 'master'

    def test_branch_field_invalid(self):
        """This field is a string."""
        data = {'branch': 123}
        with pytest.raises(TypeError):
            _ = wrappers.Manifest(data).branch  # noqa

    def test_branch_field_valid(self):
        """When value is valid."""
        data = {'branch': 'stable'}
        assert wrappers.Manifest(data).branch == 'stable'

    def test_set_branch_field(self):
        """Test the setter."""
        data = {}
        manifest = wrappers.Manifest(data)
        branch = 'my-branch'
        manifest.branch = branch
        assert data['branch'] == manifest.branch == branch

        with pytest.raises(TypeError):
            manifest.branch = 123
        assert data['branch'] == manifest.branch == branch

    def test_str_no_data(self):
        """Empty data provide no id but the branch has a default."""
        assert str(wrappers.Manifest()) == '<Manifest: id=None, branch=master>'

    def test_str_invalid_id_and_branch(self):
        """Don't care about types for str()."""
        data = {'id': 3, 'branch': 6}
        assert str(wrappers.Manifest(data)) == '<Manifest: id=3, branch=6>'

    def test_str_valid_id_and_branch(self):
        """All right."""
        data = {'id': 'eu.tiliado.App', 'branch': 'stable'}
        assert str(wrappers.Manifest(data)) \
            == '<Manifest: id=eu.tiliado.App, branch=stable>'
