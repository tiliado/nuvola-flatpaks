# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""This module contains the Builder class to build flatpaks."""

import json
from pathlib import Path
from shutil import rmtree

from nufb.wrappers import Manifest


class Builder:
    """
    Build a flatpak according to the manifest.

    :param build_root: The root build directory.
    :param manifest: The manifest to use to build the flatpak.
    """
    build_root: Path
    build_dir: Path
    manifest: Manifest
    manifest_json: Path
    build_name: str

    def __init__(self, build_root: Path, manifest: Manifest):
        self.build_root = build_root
        self.manifest = manifest
        self.build_name = f'{manifest.id} - {manifest.branch}'
        self.build_dir = build_root / self.build_name
        self.manifest_json = self.build_dir / (self.build_name + '.json')

    def build(self):
        """
        Build the flatpak.
        """
        try:
            self.set_up()
        finally:
            self.clean_up()

    def set_up(self):
        """Prepare the build environment."""
        try:
            rmtree(self.build_dir)
        except FileNotFoundError:
            pass
        self.build_dir.mkdir(parents=True)
        with self.manifest_json.open('w') as fh:
            json.dump(self.manifest.data, fh, indent=2)

    def clean_up(self):
        """Clean up after the build."""
        try:
            rmtree(self.build_dir)
        except FileNotFoundError:
            pass
