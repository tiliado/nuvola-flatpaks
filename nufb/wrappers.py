# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.
"""
This module contains convenience wrappers for manifest and its subitems.
"""
from typing import Optional, List, cast

from nufb import const, utils


class Manifest:
    """
    Data structure for manifest

    :param data: The raw manifest data or None to create an empty dictionary.
    """
    data: dict
    _id: Optional[str]
    _modules: Optional[List['Module']]
    _raw_modules: Optional[List[dict]]

    def __init__(self, data: Optional[dict] = None):
        if data is None:
            data = {}
        self.data = data
        self._id = None
        self._modules = None
        self._raw_modules = None

        if const.MANIFEST_ID in data and const.MANIFEST_APP_ID in data:
            raise ValueError(
                f'Only one of {const.MANIFEST_ID!r} and'
                f' {const.MANIFEST_APP_ID!r} should be present in a manifest.')

    @property
    def id(self) -> str:
        """
        A string defining the application id.
        """
        if not self._id:
            try:
                self._id = utils.ensure_string(self.data, const.MANIFEST_ID)
            except TypeError as e:
                try:
                    self._id = utils.ensure_string(
                        self.data, const.MANIFEST_APP_ID)
                except TypeError:
                    raise e from None
        return self._id

    @id.setter
    def id(self, value: str):
        utils.expect_type(value, str)
        self._id = value
        self.data[const.MANIFEST_ID] = value
        self.data.pop(const.MANIFEST_APP_ID, None)

    @property
    def branch(self) -> str:
        """
        The branch of the application, defaults to master.
        """
        return utils.ensure_string(
            self.data, const.MANIFEST_BRANCH, const.MANIFEST_BRANCH_DEFAULT)

    @branch.setter
    def branch(self, value: str):
        utils.expect_type(value, str)
        self.data[const.MANIFEST_BRANCH] = value

    @property
    def raw_modules(self) -> List[dict]:
        """
        The raw data of manifest modules.
        """
        if self._raw_modules is None:
            self._process_modules()
        return cast(List[dict], self._raw_modules)

    @property
    def modules(self) -> List['Module']:
        """
        Wrapped modules of the manifest.
        """
        if self._modules is None:
            self._process_modules()
        return cast(List['Module'], self._modules)

    def _process_modules(self):
        self._raw_modules = utils.ensure_list(
            self.data, const.MANIFEST_MODULES)
        self._modules = [Module(item) for item in self._raw_modules]

    def add_module(self, module: 'Module', position: Optional[int] = None):
        """
        Ann new module.

        :param module: The module to add.
        :param position: The position to insert at or `None` to append at
            the end.
        """
        raw_modules = self.raw_modules
        modules = self.modules
        if position is None:
            raw_modules.append(module.data)
            modules.append(module)
        else:
            raw_modules.insert(position, module.data)
            modules.insert(position, module)

    def find_module(self, name: str) -> Optional['Module']:
        """
        Find module by name.

        :param name: The name of a module.
        :return: The module if it has been found, `None` otherwise.
        """
        for module in self.modules:
            try:
                if module.name == name:
                    return module
            except TypeError:
                pass  # no name
        return None

    def __str__(self) -> str:
        data = self.data
        app_id = data.get(const.MANIFEST_ID, data.get(const.MANIFEST_APP_ID))
        branch = data.get(const.MANIFEST_BRANCH, const.MANIFEST_BRANCH_DEFAULT)
        return f'<Manifest: id={app_id}, branch={branch}>'


class Module:
    """
    Data structure for a manifest module.

    :param data: The raw manifest module data or None to create an empty
        dictionary.
    """
    def __init__(self, data: Optional[dict] = None):
        if data is None:
            data = {}
        self.data = data

    @property
    def name(self) -> str:
        """
        The name of the module, used in e.g. build logs.
        """
        return utils.ensure_string(self.data, const.MODULE_NAME)

    @name.setter
    def name(self, value: str):
        utils.expect_type(value, str)
        self.data[const.MODULE_NAME] = value

    def __str__(self) -> str:
        return f'<Module: name={self.data.get(const.MODULE_NAME)}>'
