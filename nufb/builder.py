# Copyright 2019-2020 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Individual build profiles."""
import asyncio
import json
import os
from asyncio import Lock, BoundedSemaphore
from os.path import expandvars, expanduser
from pathlib import Path
from typing import Dict, Any

from nufb import utils, fs
from nufb.manifest import Manifest
from nufb.logging import get_logger
from nufb.utils import exec_subprocess

LOGGER = get_logger(__name__)


class Locks:
    def __init__(self):
        self.download = Lock()
        self.build = Lock()
        self.export = Lock()
        self.install = Lock()


class Builder:
    """
    Build a flatpak according to the manifest.
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

    def __init__(self, build_root: Path, resources_dir: Path, manifest: Manifest, config: dict, locks: Locks):
        self.locks = locks
        self.repo_dir = Path(expandvars(expanduser(config["repository"]))).absolute()
        self.key_id = config["key_id"]
        self.resources_dir = resources_dir
        self.manifest = manifest
        self.name = f'{manifest.id}-{manifest.branch}'
        self.build_root = build_root
        self.build_dir = build_root / self.name
        self.result_dir = self.build_dir / 'result'
        self.global_state_dir = build_root / 'flatpak-builder'
        self.working_state_dir = self.build_dir / '.flatpak-builder'
        self.manifest_json = self.build_dir / (self.name + '.json')

    async def build(
            self,
            keep_build_dirs: bool = False,
            delete_build_dirs: bool = False,
            export: bool = None,
    ):
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
            await self.set_up()
            await self.copy_resources()
            await self.build_flatpak(
                keep_build_dirs=keep_build_dirs,
                delete_build_dirs=delete_build_dirs,
                require_changes=export is not True,
            )

            if export is not False:
                await self.export_flatpak()
            else:
                LOGGER.info("Export skipped as requested.")

            # Build dir is deleted on success by default.
            clean_up = not keep_build_dirs
        except Exception:
            clean_up = False
            raise
        finally:
            if clean_up:
                await self.clean_up()

    async def set_up(self):
        """
        Prepare the build environment.

        :raise OSError: When a filesystem operation fails.
        """
        try:
            await fs.rmtree(self.build_dir)
        except FileNotFoundError:
            pass
        await fs.makedirs(self.build_dir, exist_ok=True)
        self.manifest.process_stage_keep_rules()

    async def copy_resources(self):
        """
        Copy resources to the build directory.

        :raise OSError: When a filesystem operation fails.
        """

        async def task(source_path, destination_path):
            try:
                await fs.remove(destination_path)
            except FileNotFoundError:
                pass
            await fs.makedirs(destination_path.parent, exist_ok=True)
            await utils.hardlink_or_copy(source_path, destination_path)

        tasks = []

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

                tasks.append(task(self.resources_dir / path, self.build_dir / path))

        await asyncio.gather(*tasks)

    async def build_flatpak(self,
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
        data = json.dumps(self.manifest.data, indent=2)

        async with fs.open(self.manifest_json, 'w') as fh:
            await fh.write(data)
            await fh.write("\n")

        work_dir = self.build_dir

        # Use a symlink instead of --state-dir because the latter
        # makes flatpak-builder use absolute paths in ostree cache.
        global_state = self.global_state_dir
        ccache = global_state / "ccache"
        await fs.makedirs(ccache, exist_ok=True)
        async with fs.open(ccache / "ccache.conf", "w") as fh:
            await fh.write("max_size = 20.0G\n")
        local_state = self.working_state_dir
        await fs.makedirs(local_state, exist_ok=True)
        for symlink in 'cache', 'ccache', 'checksums', 'downloads', 'git':
            target = global_state / symlink
            await fs.makedirs(target, exist_ok=True)
            await fs.symlink(target, local_state / symlink)

        args = [
            str(self.result_dir.relative_to(work_dir)),
            str(self.manifest_json.relative_to(work_dir)),
        ]

        argv = ['time', 'flatpak-builder', '--download-only'] + args

        async with self.locks.download:
            LOGGER.debug("Running %s in %s.", argv, work_dir)
            code, out = await exec_subprocess(argv, cwd=work_dir)
            if code:
                LOGGER.error("%s returned %d.\n%s", argv, code, out)
                raise ValueError(code)
            else:
                LOGGER.info("%s returned %d.\n%s", argv, code, out)

        argv = ['time', 'flatpak-builder', '--ccache', "--disable-download"]
        if disable_cache:
            argv.append('--disable-cache')
        if require_changes:
            argv.append('--require-changes')
        if keep_build_dirs:
            argv.append('--keep-build-dirs')
        if delete_build_dirs:
            argv.append('--delete-build-dirs')

        argv.extend(args)

        async with self.locks.build:
            LOGGER.debug("Running %s in %s.", argv, work_dir)
            code, out = await exec_subprocess(argv, cwd=work_dir)
            if code:
                LOGGER.error("%s returned %d.\n%s", argv, code, out)
                raise ValueError(code)
            else:
                LOGGER.info("%s returned %d.\n%s", argv, code, out)

    async def export_flatpak(self):
        await fs.makedirs(self.repo_dir, exist_ok=True)
        work_dir = self.build_dir
        result_dir = work_dir / "result"
        if not await fs.isdir(result_dir):
            LOGGER.info("Nothing new to export to the repository.")
            return

        base_argv = ['time', 'flatpak', "build-export", "-v", f"--gpg-sign={self.key_id}"]

        argv = base_argv + [
            "-s",
            f"Import {self.manifest.id}.Debug//{self.manifest.branch}",
            "--files=files",
            "--metadata=metadata",
            "--exclude=/lib/debug/*",
            "--include=/lib/debug/app",
            str(self.repo_dir),
            str(result_dir),
            self.manifest.branch,
        ]

        async with self.locks.export:
            LOGGER.debug("Exporting %s app %s %s", self.manifest.id, self.manifest.branch, argv)
            code, out = await exec_subprocess(argv, cwd=work_dir)
            if code:
                LOGGER.error("%s returned %d.\n%s", argv, code, out)
                raise ValueError(code)
            else:
                LOGGER.info("%s returned %d.\n%s", argv, code, out)

        argv = base_argv + [
            "-s",
            f"Import {self.manifest.id}.Debug//{self.manifest.branch}",
            "--runtime",
            "--files=files/lib/debug",
            "--metadata=metadata.debuginfo",
            str(self.repo_dir),
            str(result_dir),
            self.manifest.branch,
        ]

        async with self.locks.export:
            LOGGER.debug("Exporting %s debuginfo %s %s", self.manifest.id, self.manifest.branch, argv)
            code, out = await exec_subprocess(argv, cwd=work_dir)
            if code:
                LOGGER.error("%s returned %d.\n%s", argv, code, out)
                raise ValueError(code)
            else:
                LOGGER.info("%s returned %d.\n%s", argv, code, out)

        argv = ["flatpak", "install", "--or-update", "--assumeyes", f"{self.manifest.id}//{self.manifest.branch}"]

        async with self.locks.install:
            LOGGER.debug("Installing or updating %s//%s %s", self.manifest.id, self.manifest.branch, argv)
            code, out = await exec_subprocess(argv, cwd=work_dir)
            if code:
                LOGGER.error("%s returned %d.\n%s", argv, code, out)
                raise ValueError(code)
            else:
                LOGGER.info("%s returned %d.\n%s", argv, code, out)

    async def clean_up(self):
        """
        Clean up after the build.

        :raise OSError: When a filesystem operation fails.
        """
        try:
            await fs.rmtree(self.build_dir)
        except FileNotFoundError:
            pass


async def build(
        locks: Locks,
        config: dict,
        build_root: Path,
        resources_dir: Path,
        manifests_dir: Path,
        manifest_id: str,
        branch: str,
        *,
        subst: Dict[str, Any] = None,
        **kwargs
) -> None:
    """
    Star a build.

    :param locks: Builder locks.
    :param subst: Manifest substitutions.
    :param config: Configuration.
    :param build_root: The root build directory.
    :param resources_dir: The directory containing build resources.
    :param manifests_dir: The directory where manifests are stored.
    :param manifest_id: The id of the manifest.
    :param branch: The branch of the manifest.
    :param kwargs: Other parameters for the builder.
    """

    LOGGER.debug('build(%s, %s, %s, %s, %s)', build_root, resources_dir,
                 manifests_dir, manifest_id, branch)

    data = await utils.load_yaml(manifests_dir / branch / (manifest_id + '.yml'), subst=subst)
    manifest = Manifest(data, branch, subst)
    builder = Builder(build_root, resources_dir, manifest, config, locks)
    await builder.build(**kwargs)


def buildcdk(
        branch: str,
        *,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    asyncio.run(build_cdk(
        branch,
        no_export=no_export,
        force_export=force_export,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
    ))


async def build_cdk(
        branch: str,
        *,
        locks: Locks = None,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    """
    Build Nuvola CDK

    :param branch: The branch to build.
    :param bool keep_build_dirs: Keep the build directories even if the
        build is successful.
    :param bool delete_build_dirs: Delete the build dirs even if the build
        fails.
    """
    if no_export:
        export = False
    elif force_export:
        export = True
    else:
        export = None
    await build(
        locks or Locks(),
        await utils.load_yaml(Path.cwd() / 'nufb.yml'),
        utils.get_user_cache_dir('nuvola-flatpaks'),
        Path.cwd() / 'resources',
        Path.cwd() / 'manifests',
        'eu.tiliado.NuvolaCdk', branch,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
        export=export,
    )


def buildadk(
        branch: str,
        *,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    asyncio.run(build_adk(
        branch,
        no_export=no_export,
        force_export=force_export,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
    ))


async def build_adk(
        branch: str,
        *,
        locks: Locks = None,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    if no_export:
        export = False
    elif force_export:
        export = True
    else:
        export = None
    await build(
        locks or Locks(),
        await utils.load_yaml(Path.cwd() / 'nufb.yml'),
        utils.get_user_cache_dir('nuvola-flatpaks'),
        Path.cwd() / 'resources',
        Path.cwd() / 'manifests',
        'eu.tiliado.NuvolaAdk', branch,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
        export=export,
    )


def buildbase(
        branch: str,
        *,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    asyncio.run(build_base(
        branch,
        no_export=no_export,
        force_export=force_export,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
    ))


async def build_base(
        branch: str,
        *,
        locks: Locks = None,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    if no_export:
        export = False
    elif force_export:
        export = True
    else:
        export = None
    await build(
        locks or Locks(),
        await utils.load_yaml(Path.cwd() / 'nufb.yml'),
        utils.get_user_cache_dir('nuvola-flatpaks'),
        Path.cwd() / 'resources',
        Path.cwd() / 'manifests',
        'eu.tiliado.NuvolaBase', branch,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
        export=export,
    )


def buildnuvola(
        branch: str,
        *,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    asyncio.run(build_nuvola(
        branch,
        no_export=no_export,
        force_export=force_export,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
    ))


async def build_nuvola(
        branch: str,
        *,
        locks: Locks = None,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    if no_export:
        export = False
    elif force_export:
        export = True
    else:
        export = None
    await build(
        locks or Locks(),
        await utils.load_yaml(Path.cwd() / 'nufb.yml'),
        utils.get_user_cache_dir('nuvola-flatpaks'),
        Path.cwd() / 'resources',
        Path.cwd() / 'manifests',
        'eu.tiliado.Nuvola', branch,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
        export=export,
    )


def buildapps(
        branch: str,
        *,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
        concurrency: int = None,
):
    asyncio.run(build_apps(
        branch,
        no_export=no_export,
        force_export=force_export,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
    ))


async def build_apps(
        branch: str,
        *,
        locks: Locks = None,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
        concurrency: int = None,
):
    config = await utils.load_yaml(Path.cwd() / 'nufb.yml')
    apps = config["apps"].get(branch)
    if apps is None:
        apps = config["apps"].get("master")
    assert apps

    if locks is None:
        locks = Locks()

    semaphore = BoundedSemaphore(concurrency or len(apps))

    async def task(name):
        async with semaphore:
            return await build_app(
                branch,
                name,
                no_export=no_export,
                force_export=force_export,
                keep_build_dirs=keep_build_dirs,
                delete_build_dirs=delete_build_dirs,
                locks=locks,
            )

    await asyncio.gather(*map(task, apps))


def buildapp(
        branch: str,
        name: str,
        *,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    return asyncio.run(build_app(
        branch,
        name,
        no_export=no_export,
        force_export=force_export,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
    ))


async def build_app(
        branch: str,
        name: str,
        *,
        locks: Locks = None,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
):
    if no_export:
        export = False
    elif force_export:
        export = True
    else:
        export = None

    if "@" in name:
        name, app_branch = name.split("@")
    else:
        app_branch = "master"

    subst = {
        "APP_ID_DASH": name,
        "APP_ID_UNDERSCORE": name.replace("-", "_"),
        "APP_ID_UNIQUE": ''.join(s.capitalize() for s in name.split("-")),
        "APP_BRANCH": app_branch,
    }
    return await build(
        locks or Locks(),
        await utils.load_yaml(Path.cwd() / 'nufb.yml'),
        utils.get_user_cache_dir('nuvola-flatpaks'),
        Path.cwd() / 'resources',
        Path.cwd() / 'manifests',
        'eu.tiliado.NuvolaApp', branch,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
        export=export,
        subst=subst,
    )
