# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Tests for nufb.builder."""

import os
from pathlib import Path

import pytest

from nufb.builder import Builder
from nufb.tests import make_file
from nufb.tests.data import MANIFEST_JSON
from nufb.wrappers import Manifest


class TestBuilder:
    """Tests for nufb.builder.Builder."""
    def test_set_up_from_scratch(self, tmp_path: Path, manifest: Manifest):
        """Test set_up() method when corresponding directories don't exist."""
        build_root = tmp_path / 'blah-blah' / 'root'
        builder = Builder(build_root, tmp_path, manifest)
        assert tmp_path.is_dir()
        assert not builder.build_dir.exists()
        builder.set_up()
        assert builder.manifest_json.read_text() == MANIFEST_JSON

    def test_set_up_dirty(self, tmp_path: Path, manifest: Manifest):
        """Test set_up() method when corresponding directories exist."""
        build_root = tmp_path / 'blah-blah' / 'root'
        builder = Builder(build_root, tmp_path, manifest)
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
        builder = Builder(build_root, tmp_path, manifest)
        assert not builder.build_dir.is_dir()
        builder.clean_up()

    def test_clean_up_dirty(self, tmp_path: Path, manifest: Manifest):
        """There is something to clean up."""
        build_root = tmp_path / 'blah-blah' / 'root'
        builder = Builder(build_root, tmp_path, manifest)
        builder.manifest_json.parent.mkdir(parents=True)
        builder.manifest_json.write_text('abc')
        builder.build_dir.is_dir()
        sub_dir = builder.build_dir / 'sub-dir'
        sub_dir.mkdir(parents=True)
        builder.clean_up()
        assert not builder.build_dir.exists()
        assert not builder.manifest_json.exists()
        assert not sub_dir.exists()

    def test_copy_resources_success(self, tmp_path: Path):
        """Copy resources without any errors."""
        files = (
            'module.json',
            'a/file.txt',
            'b/c/archive.tar.gz',
            'd/e/f/fix.patch',
        )
        data = {
            'id': 'eu.tiliado.Test',
            'modules': [
                {
                    'sources': [
                        files[0],
                        {
                            'type': 'file',
                            'path': files[1]
                        }
                    ]
                }, {
                    'sources': [
                        {
                            'type': 'archive',
                            'path': files[2]
                        },
                        {
                            'type': 'patch',
                            'path': files[3]
                        },
                        {
                            'type': 'archive',
                            'url': 'http://www.valgrind.org/valgrind.tar.bz2'
                        }
                    ]
                },
            ]
        }
        build_root = tmp_path / 'blah-blah' / 'root'
        resources_dir = tmp_path / 'blah-blah2' / 'resources'
        for path in files:
            make_file(resources_dir / path)
        manifest = Manifest(data)
        builder = Builder(build_root, resources_dir, manifest)
        builder.copy_resources()
        for path in files:
            assert (builder.build_dir / path).read_text() \
                == os.path.basename(path)

    def test_copy_resources_missing(self, tmp_path: Path):
        """Fail to copy missing resources."""
        data = {
            'id': 'eu.tiliado.Test',
            'modules': [{'sources': ['not-found.json']}]
        }
        build_root = tmp_path / 'blah-blah' / 'root'
        resources_dir = tmp_path / 'blah-blah2' / 'resources'
        manifest = Manifest(data)
        builder = Builder(build_root, resources_dir, manifest)
        with pytest.raises(FileNotFoundError):
            builder.copy_resources()

    def test_copy_resources_directory(self, tmp_path: Path):
        """Fail to copy missing resources."""
        data = {
            'id': 'eu.tiliado.Test',
            'modules': [{'sources': ['not-found.json']}]
        }
        build_root = tmp_path / 'blah-blah' / 'root'
        resources_dir = tmp_path / 'blah-blah2' / 'resources'
        manifest = Manifest(data)
        builder = Builder(build_root, resources_dir, manifest)
        with pytest.raises(FileNotFoundError):
            builder.copy_resources()
