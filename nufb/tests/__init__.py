# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Utility functions for test cases."""

from pathlib import Path
from typing import Optional


def make_file(path: Path, content: Optional[str] = None) -> None:
    """
    Create a file with parent directories.

    :param path: The path to file.
    :param content: The content of the file. If not specified, the basename
        will be used instead.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(path.name) if content is None else content)
