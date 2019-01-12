# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Tests for nufb.builder."""

from pathlib import Path

from nufb.builder import Builder
from nufb.tests.data import MANIFEST_JSON
from nufb.wrappers import Manifest


class TestBuilder:
    """Tests for nufb.builder.Builder."""
    def test_set_up_from_scratch(self, tmp_path: Path, manifest: Manifest):
        """Test set_up() method when corresponding directories don't exist."""
        build_root = tmp_path / 'blah-blah' / 'root'
        builder = Builder(build_root, manifest)
        assert tmp_path.is_dir()
        assert not builder.build_dir.exists()
        builder.set_up()
        assert builder.manifest_json.read_text() == MANIFEST_JSON

    def test_set_up_dirty(self, tmp_path: Path, manifest: Manifest):
        """Test set_up() method when corresponding directories exist."""
        build_root = tmp_path / 'blah-blah' / 'root'
        builder = Builder(build_root, manifest)
        builder.manifest_json.parent.mkdir(parents=True)
        builder.manifest_json.write_text('abc')
        sub_dir = builder.build_dir / 'sub-dir'
        sub_dir.mkdir(parents=True)
        assert builder.build_dir.is_dir()
        builder.set_up()
        assert builder.build_dir.is_dir()
        assert not sub_dir.exists()
        assert builder.manifest_json.read_text() == MANIFEST_JSON

    def test_clean_up_nothing(self, tmp_path: Path, manifest: Manifest):
        """No error if there is nothing to clean up."""
        build_root = tmp_path / 'blah-blah' / 'root'
        builder = Builder(build_root, manifest)
        assert not builder.build_dir.is_dir()
        builder.clean_up()

    def test_clean_up_dirty(self, tmp_path: Path, manifest: Manifest):
        """There is something to clean up."""
        build_root = tmp_path / 'blah-blah' / 'root'
        builder = Builder(build_root, manifest)
        builder.manifest_json.parent.mkdir(parents=True)
        builder.manifest_json.write_text('abc')
        builder.build_dir.is_dir()
        sub_dir = builder.build_dir / 'sub-dir'
        sub_dir.mkdir(parents=True)
        builder.clean_up()
        assert not builder.build_dir.exists()
        assert not builder.manifest_json.exists()
        assert not sub_dir.exists()
