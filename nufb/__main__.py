from __future__ import annotations

import sys

import clizy

import nufb


def main() -> int:
    """Main entrypoint."""

    if sys.argv[0].endswith("__main__.py"):
        sys.argv[0] = "nufbctl"

    clizy.run_funcs(version)
    return 0


def version() -> None:
    """Print version."""
    print("nufb", nufb.__version__)


if __name__ == "__main__":
    sys.exit(main())
