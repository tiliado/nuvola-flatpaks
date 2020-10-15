import os
import shutil
from typing import Callable, cast

from aiofiles import open as _open
from aiofiles.os import wrap
from aiofiles.threadpool import AsyncTextIOWrapper  # type: ignore


class AsyncTextIO(AsyncTextIOWrapper):
    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc, tb):
        ...


open = cast(Callable[..., AsyncTextIO], _open)

remove = wrap(os.remove)
makedirs = wrap(os.makedirs)
hardlink = wrap(os.link)
rmtree = wrap(shutil.rmtree)
copy = wrap(shutil.copy2)
symlink = wrap(os.symlink)
isdir = wrap(os.path.isdir)

__all__ = ["open", "remove", "rmtree", "makedirs", "hardlink", "copy", "symlink", "isdir"]
