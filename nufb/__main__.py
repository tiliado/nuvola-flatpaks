from __future__ import annotations

import sys

import clizy

import nufb
from nufb.builder import buildcdk, buildbase
from nufb.logging import init_logging


def main() -> int:
    """Main entrypoint."""

    if sys.argv[0].endswith("__main__.py"):
        sys.argv[0] = "nufbctl"

    init_logging()
    clizy.run_funcs(buildcdk, buildbase, version)
    return 0


def version() -> None:
    """Print version."""
    print("nufb", nufb.__version__)


if __name__ == "__main__":
    sys.exit(main())
