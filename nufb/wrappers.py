# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.
"""
This module contains convenience wrappers for manifest and its subitems.
"""
from typing import Optional

from nufb import const, utils


class Manifest:
    """
    Data structure for manifest

    :param data: The raw manifest data or None to create an empty dictionary.
    """
    data: dict
    _id: Optional[str]

    def __init__(self, data: Optional[dict] = None):
        if data is None:
            data = {}
        self.data = data
        self._id = None
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

    def __str__(self) -> str:
        data = self.data
        app_id = data.get(const.MANIFEST_ID, data.get(const.MANIFEST_APP_ID))
        branch = data.get(const.MANIFEST_BRANCH, const.MANIFEST_BRANCH_DEFAULT)
        return f'<Manifest: id={app_id}, branch={branch}>'
