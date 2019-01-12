# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""This module contains the Builder class to build flatpaks."""

import json
import os
from pathlib import Path
from shutil import rmtree

from nufb import utils
from nufb.wrappers import Manifest


class Builder:
    """
    Build a flatpak according to the manifest.

    :param build_root: The root build directory.
    :param resources_dir: The directory containing build resources.
    :param manifest: The manifest to use to build the flatpak.
    """
    resources_dir: Path
    manifest: Manifest
    build_name: str
    paths: 'BuildPaths'

    def __init__(self, build_root: Path, resources_dir: Path,
                 manifest: Manifest):
        self.resources_dir = resources_dir
        self.manifest = manifest
        self.build_name = f'{manifest.id}-{manifest.branch}'
        self.paths = BuildPaths(build_root, self.build_name)

    def build(self):
        """
        Build the flatpak.

        :raise OSError: When a filesystem operation fails.
        """
        try:
            self.set_up()
            self.copy_resources()
        finally:
            self.clean_up()

    def set_up(self):
        """
        Prepare the build environment.

        :raise OSError: When a filesystem operation fails.
        """
        try:
            rmtree(self.paths.build_dir)
        except FileNotFoundError:
            pass
        self.paths.build_dir.mkdir(parents=True)
        with self.paths.manifest.open('w') as fh:
            json.dump(self.manifest.data, fh, indent=2)

    def copy_resources(self):
        """
        Copy resources to the build directory.

        :raise OSError: When a filesystem operation fails.
        """
        for module in self.manifest.modules:
            for source in module.sources:
                if isinstance(source, str):
                    path = source
                elif source['type'] in ('file', 'patch', 'archive'):
                    path = source.get('path')
                else:
                    continue

                if not path or os.path.isabs(path):
                    continue

                source_path = self.resources_dir / path
                destination_path = self.paths.build_dir / path
                try:
                    destination_path.unlink()
                except FileNotFoundError:
                    pass
                destination_path.parent.mkdir(parents=True, exist_ok=True)
                utils.hardlink_or_copy(source_path, destination_path)

    def clean_up(self):
        """
        Clean up after the build.

        :raise OSError: When a filesystem operation fails.
        """
        try:
            rmtree(self.paths.build_dir)
        except FileNotFoundError:
            pass


class BuildPaths:
    """
    Data structure containing various build paths.

    :param build_root: The root build directory.
    :param build_name: The name of a build.
    """
    build_root: Path
    build_dir: Path
    result_dir: Path
    state_dir: Path
    manifest: Path

    def __init__(self, build_root: Path, build_name: str):
        self.build_root = build_root
        self.build_dir = build_root / build_name
        self.result_dir = self.build_dir / 'result'
        self.state_dir = build_root / 'flatpak-builder'
        self.manifest = self.build_dir / (build_name + '.json')
