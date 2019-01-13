# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.
"""
This module contains Task class.
"""
from pathlib import Path

from nufb.wrappers import Manifest


# pylint: disable=too-many-instance-attributes
class Task:
    """
    Data structure containing task details.

    :param build_root: The root build directory.
    :param resources_dir: The directory containing build resources.
    :param manifest: The manifest to use to build the flatpak.
    """
    manifest: Manifest
    name: str
    resources_dir: Path
    build_root: Path
    build_dir: Path
    result_dir: Path
    global_state_dir: Path
    working_state_dir: Path
    manifest_json: Path

    def __init__(self, build_root: Path, resources_dir: Path,
                 manifest: Manifest):
        self.resources_dir = resources_dir
        self.manifest = manifest
        self.name = f'{manifest.id}-{manifest.branch}'
        self.build_root = build_root
        self.build_dir = build_root / self.name
        self.result_dir = self.build_dir / 'result'
        self.global_state_dir = build_root / 'flatpak-builder'
        self.working_state_dir = self.build_dir / '.flatpak-builder'
        self.manifest_json = self.build_dir / (self.name + '.json')
