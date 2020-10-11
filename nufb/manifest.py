from typing import List,  Union

from nufb import const


class Manifest:
    def __init__(self, data: dict, branch: str = const.MANIFEST_BRANCH_DEFAULT):
        self.branch = branch
        self.data = data
        modules = data.get(const.MANIFEST_MODULES)
        if modules is None:
            self.data[const.MANIFEST_MODULES] = modules = []
        self.modules = {m.get(const.MODULE_NAME): m for m in modules if isinstance(m, dict)}

        if self.data.setdefault(const.MANIFEST_BRANCH, branch) != branch:
            raise ValueError(f"Wrong branch in manifest: {self.data[const.MANIFEST_BRANCH]}")

    @property
    def id(self) -> str:
        """
        A string defining the application id.

        :type: str
        :raise TypeError: Invalid type.
        """
        return self.data[const.MANIFEST_APP_ID]

    def sources(self, module_name: str, create: bool = True) -> List[Union[str, dict]]:
        module = self.modules[module_name]
        sources = module.get(const.MODULE_SOURCES)

        if sources is None:
            sources = []
            if create:
                module[const.MODULE_SOURCES] = sources

        return sources
