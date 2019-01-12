# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Tests for nufb.wrappers"""
import pytest

from nufb import wrappers


# pylint: disable=too-many-public-methods
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

    def test_raw_modules_no_data(self):
        """When no modules are in manifest, an empty list is created."""
        data = {}
        manifest = wrappers.Manifest(data)
        assert manifest.raw_modules == []
        assert id(manifest.raw_modules) == id(data['modules'])

    def test_raw_modules_empty(self):
        """When an empty modules array is manifest, it is unmodified."""
        modules = []
        data = {'modules': modules}
        manifest = wrappers.Manifest(data)
        assert manifest.raw_modules == modules == []
        assert id(manifest.raw_modules) == id(data['modules']) == id(modules)

    def test_raw_modules_not_empty(self):
        """When a non-empty modules array is manifest, it is unmodified."""
        module = {'name': None}
        modules = [module]
        data = {'modules': modules}
        manifest = wrappers.Manifest(data)
        assert manifest.raw_modules == modules == [module]
        assert id(manifest.raw_modules) == id(data['modules']) == id(modules)

    def test_modules_no_data(self):
        """When no modules are in manifest, an empty list is created."""
        data = {}
        manifest = wrappers.Manifest(data)
        assert manifest.modules == []
        assert id(manifest.modules) != id(data['modules'])

    def test_modules_empty(self):
        """
        When an empty modules array is manifest, an empty list is created.
        """
        modules = []
        data = {'modules': modules}
        manifest = wrappers.Manifest(data)
        assert manifest.modules == []
        assert id(manifest.modules) != id(modules)

    def test_modules_not_empty(self):
        """
        When a non-empty modules array is manifest, a non-empty list is
        created.
        """
        module = {'name': 'my-name'}
        modules = [module]
        data = {'modules': modules}
        manifest = wrappers.Manifest(data)
        assert manifest.modules != [module]
        assert id(manifest.modules) != id(data['modules'])
        assert manifest.modules[0].data == module
        assert id(manifest.modules[0].data) == id(module)

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

    def test_add_module(self):
        """Add module at various positions."""
        module = wrappers.Module()

        manifest = wrappers.Manifest()
        manifest.add_module(module, -123)
        assert len(manifest.modules) == 1
        assert manifest.modules[0] == module

        manifest = wrappers.Manifest()
        assert not manifest.modules
        manifest.add_module(module)
        assert len(manifest.modules) == 1
        assert manifest.modules[0] == module

        modules = [{}, {}, {}, {}]
        data = {'modules': modules}
        manifest = wrappers.Manifest(data)
        manifest.add_module(module, 0)
        assert len(manifest.modules) == 5
        assert manifest.modules[0] == module
        manifest.add_module(module, -2)
        assert len(manifest.modules) == 6
        assert manifest.modules[3] == module
        manifest.add_module(module)
        assert len(manifest.modules) == 7
        assert manifest.modules[6] == module

    def test_find_module(self):
        """Find a module"""
        name = 'my-module'
        module = {'name': name}
        data = {'modules': [module]}
        assert wrappers.Manifest().find_module(name) is None
        assert id(wrappers.Manifest(data).find_module(name).data) == id(module)

    def test_init_module(self):
        """Initialization module."""
        assert wrappers.Manifest().init_module.name == 'init'
        module = {'name': 'init'}
        data = {'modules': [module]}
        assert id(wrappers.Manifest(data).init_module.data) == id(module)

    def test_finish_module(self):
        """Finish module."""
        assert wrappers.Manifest().finish_module.name == 'finish'
        module = {'name': 'finish'}
        data = {'modules': [module]}
        assert id(wrappers.Manifest(data).finish_module.data) == id(module)


class TestModule:
    """Tests for nufb.wrappers.Module"""
    def test_construct(self):
        """Test init method."""
        assert wrappers.Module().data == {}
        data = {}
        assert id(wrappers.Module(data).data) == id(data)

    def test_new(self):
        """New module"""
        name = 'my-module'
        module = wrappers.Module.new(name, size=10)
        assert module.name == name
        assert module.data['size'] == 10

    def test_name_field(self):
        """Test name getter and setter"""
        module = wrappers.Module()
        with pytest.raises(TypeError):
            _ = module.name   # noqa

        name = 'my-module'
        module.name = name
        assert module.name == name

        with pytest.raises(TypeError):
            module.name = 123
        assert module.name == name

    @pytest.mark.parametrize('field,key,values', [
        ('sources', None, [{'path': 'file.txt'}]),
        ('build_commands', None, [{'path': 'file.txt'}]),
    ])
    def test_fields_of_type_list(self, field: str, key: str, values: list):
        """Properties which return a list."""
        if not key:
            key = field.replace('_', '-')

        assert getattr(wrappers.Module(), field) == []

        empty: list = []
        data: dict = {key: empty}
        module = wrappers.Module(data)
        result = getattr(module, field)
        assert result == []
        assert id(result) == id(empty)

        data = {key: values}
        original_values = values[:]
        module = wrappers.Module(data)
        result = getattr(module, field)
        assert result == original_values
        assert id(result) == id(values)

        data = {key: 123456}
        with pytest.raises(TypeError):
            getattr(wrappers.Module(data), field)

    def test_str(self):
        """str() shouldn't raise an error"""
        assert str(wrappers.Module()) == '<Module: name=None>'
        assert str(wrappers.Module({'name': 123})) == '<Module: name=123>'
        assert str(wrappers.Module({'name': 'abc'})) == '<Module: name=abc>'
