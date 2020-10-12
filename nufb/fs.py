import os
import shutil

import aiofiles.os
from aiofiles import open

remove = aiofiles.os.remove
makedirs = aiofiles.os.wrap(os.makedirs)
hardlink = aiofiles.os.wrap(os.link)
rmtree = aiofiles.os.wrap(shutil.rmtree)
copy = aiofiles.os.wrap(shutil.copy2)
symlink = aiofiles.os.wrap(os.symlink)
isdir = aiofiles.os.wrap(os.path.isdir)

__all__ = ["open", "remove", "rmtree", "makedirs", "hardlink", "copy", "symlink", "isdir"]
