# Copyright 2019-2020 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Individual build profiles."""
import json
import os
import subprocess
from pathlib import Path
from shutil import rmtree

from nufb import utils
from nufb.manifest import Manifest
from nufb.logging import get_logger

LOGGER = get_logger(__name__)


class Builder:
    """
    Build a flatpak according to the manifest.

    :param task: The build task.
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

    def __init__(self, build_root: Path, resources_dir: Path, manifest: Manifest):
        self.resources_dir = resources_dir
        self.manifest = manifest
        self.name = f'{manifest.id}-{manifest.branch}'
        self.build_root = build_root
        self.build_dir = build_root / self.name
        self.result_dir = self.build_dir / 'result'
        self.global_state_dir = build_root / 'flatpak-builder'
        self.working_state_dir = self.build_dir / '.flatpak-builder'
        self.manifest_json = self.build_dir / (self.name + '.json')

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
            rmtree(self.build_dir)
        except FileNotFoundError:
            pass
        self.build_dir.mkdir(parents=True)

    def copy_resources(self):
        """
        Copy resources to the build directory.

        :raise OSError: When a filesystem operation fails.
        """
        for module in self.manifest.modules:
            for source in self.manifest.sources(module, create=False):
                if isinstance(source, str):
                    path = source
                elif source['type'] in ('file', 'patch', 'archive'):
                    path = source.get('path')
                else:
                    continue

                if not path or os.path.isabs(path):
                    continue

                source_path = self.resources_dir / path
                destination_path = self.build_dir / path
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
        with self.manifest_json.open('w') as fh:
            json.dump(self.manifest.data, fh, indent=2)
            fh.write("\n")

        work_dir = self.build_dir

        # Use a symlink instead of --state-dir because the latter
        # makes flatpak-builder use absolute paths in ostree cache.
        global_state = self.global_state_dir
        global_state.mkdir(exist_ok=True)
        local_state = self.working_state_dir
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
            str(self.result_dir.relative_to(work_dir)),
            str(self.manifest_json.relative_to(work_dir))])

        LOGGER.debug("Running %s in %s.", argv, work_dir)
        subprocess.run(argv, cwd=work_dir, check=True)

    def clean_up(self):
        """
        Clean up after the build.

        :raise OSError: When a filesystem operation fails.
        """
        try:
            rmtree(self.build_dir)
        except FileNotFoundError:
            pass


def build(build_root: Path, resources_dir: Path, manifests_dir: Path,
          manifest_id: str, branch: str, **kwargs) -> None:
    """
    Star a build.

    :param build_root: The root build directory.
    :param resources_dir: The directory containing build resources.
    :param manifests_dir: The directory where manifests are stored.
    :param manifest_id: The id of the manifest.
    :param branch: The branch of the manifest.
    :param kwargs: Other parameters for the builder.
    """

    LOGGER.debug('build(%s, %s, %s, %s, %s)', build_root, resources_dir,
                 manifests_dir, manifest_id, branch)

    data = utils.load_yaml(manifests_dir / branch / (manifest_id + '.yml'))
    manifest = Manifest(data, branch)
    builder = Builder(build_root, resources_dir, manifest)
    builder.build(**kwargs)


def buildcdk(branch: str, *,
             keep_build_dirs: bool = False,
             delete_build_dirs: bool = False):
    """
    Build Nuvola CDK

    :param branch: The branch to build.
    :param bool keep_build_dirs: Keep the build directories even if the
        build is successful.
    :param bool delete_build_dirs: Delete the build dirs even if the build
        fails.
    """
    build(
        utils.get_user_cache_dir('nuvola-flatpaks'),
        Path.cwd() / 'resources',
        Path.cwd() / 'manifests',
        'eu.tiliado.NuvolaCdk', branch,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs
    )
