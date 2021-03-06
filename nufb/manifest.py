from typing import Any, Dict, List, Union, cast

from nufb import const
from nufb.utils import get_data_path

FILE_CHECK_MODULE = {
    const.MODULE_NAME: "nufb-filelist",
    const.MODULE_BUILD_SYSTEM: const.BUILD_SYSTEM_SIMPLE,
    const.MODULE_BUILD_COMMANDS: [
        "mkdir -p /app/lib/debug/filelist",
        "test -f /app/lib/debug/filelist/filelist || cp filelist.py /app/lib/debug/filelist/filelist",  # noqa: SC300
        "test -e /app/lib/debug/filelist/latest || touch /app/lib/debug/filelist/latest",
    ],
    const.MODULE_SOURCES: [{"type": "file", "path": str(get_data_path("filelist.py"))}],
}


class Manifest:
    modules: Dict[str, dict]

    def __init__(
        self,
        data: dict,
        branch: str = const.MANIFEST_BRANCH_DEFAULT,
        subst: Dict[str, Any] = None,
    ):
        self.subst = subst
        self.branch = branch
        self.data = data
        modules = data.get(const.MANIFEST_MODULES)
        if modules is None:
            self.data[const.MANIFEST_MODULES] = modules = []
        self.modules = {cast(str, m[const.MODULE_NAME]): m for m in modules if isinstance(m, dict)}

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

    def process_stage_keep_rules(self) -> None:
        keep_files = ["/app/lib/debug/*"]
        last_module = self.data[const.MANIFEST_MODULES][-1]

        for name, module in self.modules.items():
            if module.get(const.MODULE_DISABLED):
                assert module != last_module
                continue

            try:
                post_install = module[const.MODULE_POST_INSTALL]
            except KeyError:
                module[const.MODULE_POST_INSTALL] = post_install = []

            sources = self.sources(name, create=True)
            stage = module.pop(const.STAGE_PATTERNS, [])
            stage.append("@/app/lib/debug/*")
            keep = module.pop(const.KEEP_PATTERNS, [])
            stage += keep
            keep_files += keep

            if module != last_module:
                post_install.append(
                    "cd /app/lib/debug/filelist && "  # noqa: SC300
                    "./filelist /app $FLATPAK_BUILDER_BUILDDIR/allowed latest > current && "  # noqa: SC300
                    "mv current latest"  # noqa: SC300
                )

                sources.append(
                    {
                        "type": "script",
                        "dest-filename": "allowed",
                        "commands": stage,
                    }
                )
            else:
                post_install.append(  # noqa: SC300
                    "cd /app/lib/debug/filelist && "
                    "rm latest && "
                    "./filelist /app $FLATPAK_BUILDER_BUILDDIR/allowed /dev/null > latest"  # noqa: SC300
                )

                sources.append(
                    {
                        "type": "script",
                        "dest-filename": "allowed",
                        "commands": keep_files,
                    }
                )

        self.data[const.MANIFEST_MODULES].insert(0, FILE_CHECK_MODULE)
        self.modules["nufb-filelist"] = FILE_CHECK_MODULE
