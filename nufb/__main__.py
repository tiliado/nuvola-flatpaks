import asyncio
import sys

import clizy

import nufb
from nufb.builder import build_cdk, build_adk, build_base, build_nuvola, build_apps, build_app, build_all
from nufb.logging import init_logging


def main() -> int:
    """Main entrypoint."""

    if sys.argv[0].endswith("__main__.py"):
        sys.argv[0] = "nufbctl"

    init_logging()
    clizy.run_funcs(buildall, buildcdk, buildadk, buildbase, buildnuvola, buildapp, buildapps, version)
    return 0


def version() -> None:
    """Print version."""
    print("nufb", nufb.__version__)


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
        concurrency=concurrency,
    ))


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


def buildall(
        branch: str,
        *,
        no_export: bool = False,
        force_export: bool = False,
        keep_build_dirs: bool = False,
        delete_build_dirs: bool = False,
        concurrency: int = None,
):
    asyncio.run(build_all(
        branch,
        no_export=no_export,
        force_export=force_export,
        keep_build_dirs=keep_build_dirs,
        delete_build_dirs=delete_build_dirs,
        concurrency=concurrency,
    ))


if __name__ == "__main__":
    sys.exit(main())
