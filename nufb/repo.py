from os import fspath
from os.path import expanduser, expandvars
from pathlib import Path

from nufb import fs
from nufb.logging import get_logger
from nufb.utils import exec_subprocess

LOGGER = get_logger(__name__)


async def update_repo(config: dict) -> None:
    repository = config["repository"]
    repo_dir = Path(expandvars(expanduser(repository["path"]))).absolute()
    key_id = repository["key_id"]
    branch = repository.get("default_branch", "stable")
    name = repository["name"]

    await fs.makedirs(repo_dir, exist_ok=True)

    argv = [
        "time",
        "flatpak",
        "build-update-repo",
        "-vv",
        f"--title={name}",
        f"--default-branch={branch}",
        f"--gpg-sign={key_id}",
        fspath(repo_dir),
    ]

    LOGGER.debug("Running %s in %s.", argv, repo_dir)
    code, out = await exec_subprocess(argv, cwd=repo_dir)
    if code:
        LOGGER.error("%s returned %d.\n%s", argv, code, out)
        raise ValueError(code)
    else:
        LOGGER.info("%s returned %d.\n%s", argv, code, out)
