# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Individual build profiles."""

from pathlib import Path

from nufb import utils
from nufb.builder import Builder
from nufb.wrappers import Manifest


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

    data = utils.load_yaml(manifests_dir / branch / (manifest_id + '.yaml'))
    manifest = Manifest(data)

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
        Path.cwd() / 'data',
        Path.cwd() / 'manifests',
        'eu.tiliado.NuvolaCdk', branch,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs
    )
