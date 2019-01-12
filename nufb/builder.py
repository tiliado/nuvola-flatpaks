# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""This module contains the Builder class to build flatpaks."""

import json
import os
import subprocess
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

    def build(self,
              keep_build_dirs: bool = False,
              delete_build_dirs: bool = False):
        """
        Build the flatpak.

        :param bool keep_build_dirs: Keep the build directories even if the
            build is successful.
        :param bool delete_build_dirs: Delete the build dirs even if the build
            fails.
        :raise OSError: When a filesystem operation fails.
        """
        # Build dir is kept on failure by default.
        clean_up = delete_build_dirs
        try:
            self.set_up()
            self.copy_resources()
            self.build_flatpak(keep_build_dirs=keep_build_dirs,
                               delete_build_dirs=delete_build_dirs)
            # Build dir is deleted on success by default.
            clean_up = not keep_build_dirs
        finally:
            if clean_up:
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

    def build_flatpak(self,
                      disable_cache: bool = False,
                      require_changes: bool = True,
                      keep_build_dirs: bool = False,
                      delete_build_dirs: bool = False,
                      ) -> None:
        """
        Build the flatpak with flatpak-builder.

        :param disable_cache: Don't look at the existing cache for a previous
            build, instead always rebuild modules.
        :param require_changes: Do nothing if nothing changes since last cached
            build.
        :param bool keep_build_dirs: Keep the build directories even if the
            build is successful.
        :param bool delete_build_dirs: Delete the build dirs even if the build
            fails.
        """
        work_dir = self.paths.build_dir

        # Use a symlink instead of --state-dir because the latter
        # makes flatpak-builder use absolute paths in ostree cache.
        global_state = self.paths.global_state_dir
        global_state.mkdir(exist_ok=True)
        local_state = self.paths.working_state_dir
        local_state.mkdir(exist_ok=True)
        for symlink in 'cache', 'ccache', 'checksums', 'downloads', 'git':
            target = global_state / symlink
            target.mkdir(exist_ok=True)
            (local_state / symlink).symlink_to(target)

        argv = ['time', 'flatpak-builder', '--ccache']
        if disable_cache:
            argv.append('--disable-cache')
        if require_changes:
            argv.append('--require-changes')
        if keep_build_dirs:
            argv.append('--keep-build-dirs')
        if delete_build_dirs:
            argv.append('--delete-build-dirs')

        argv.extend([
            str(self.paths.result_dir.relative_to(work_dir)),
            str(self.paths.manifest.relative_to(work_dir))])

        print(argv)
        subprocess.run(argv, cwd=str(work_dir))

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
    global_state_dir: Path
    working_state_dir: Path
    manifest: Path

    def __init__(self, build_root: Path, build_name: str):
        self.build_root = build_root
        self.build_dir = build_root / build_name
        self.result_dir = self.build_dir / 'result'
        self.global_state_dir = build_root / 'flatpak-builder'
        self.working_state_dir = self.build_dir / '.flatpak-builder'
        self.manifest = self.build_dir / (build_name + '.json')
