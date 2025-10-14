# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import unittest
from unittest import mock
import io
import tempfile
from pathlib import Path

import yaml

from racksdb.generic.db import (
    DBFileLoader,
    DBSplittedFilesLoader,
    DBStdinLoader,
    DBStringLoader,
    GenericDB,
)
from racksdb.generic.errors import DBFormatError

from .lib.common import VALID_DB, valid_schema
from .lib import bases

COMPOSER_ERROR_STR = "*fail:{:"


class TestDBLoaderBase(unittest.TestCase):
    def assertLoaderContent(self, loader):
        self.assertCountEqual(
            loader.content.keys(), ["apples", "pear", "bananas", "stock"]
        )
        # apples can either be a list (with key name attribute) or a dict with name as
        # keys.
        try:
            self.assertIsInstance(loader.content["apples"], list)
        except AssertionError:
            self.assertIsInstance(loader.content["apples"], dict)
        self.assertIsInstance(loader.content["pear"], dict)
        self.assertIsInstance(loader.content["bananas"], list)
        self.assertIsInstance(loader.content["stock"], dict)

        # Test loaded DB is valid for the schema
        db = GenericDB("Test", valid_schema(), bases)
        db.load(loader)


class TestDBFileLoader(TestDBLoaderBase):
    def write_db_file(self, content):
        self.tmp = tempfile.NamedTemporaryFile(mode="w", delete=False)
        self.tmp.write(content)
        self.tmp.close()

    def tearDown(self):
        Path(self.tmp.name).unlink()

    def test_load(self):
        self.write_db_file(yaml.dump(VALID_DB))
        self.assertLoaderContent(DBFileLoader(Path(self.tmp.name)))

    def test_load_composer_error(self):
        self.write_db_file(COMPOSER_ERROR_STR)
        with self.assertRaisesRegex(DBFormatError, "^found undefined alias .*"):
            DBFileLoader(Path(self.tmp.name))


class TestDBSplittedFilesLoader(TestDBLoaderBase):
    def test_load(self):
        # Split VALID_DB in multiple files and load the directory.
        with tempfile.TemporaryDirectory() as _tmpdir:
            tmpdir = Path(_tmpdir)
            (tmpdir / "apples").mkdir()
            for apple in VALID_DB["apples"]:
                with open(tmpdir / "apples" / f"{apple['name']}.yaml", "w+") as fh:
                    fh.write(
                        yaml.dump(
                            {
                                key: value
                                for key, value in apple.items()
                                if key != "name"
                            }
                        )
                    )
            with open(tmpdir / "pear.yaml", "w+") as fh:
                fh.write(yaml.dump(VALID_DB["pear"]))
            (tmpdir / "bananas.l").mkdir()
            for banana in VALID_DB["bananas"]:
                with open(
                    tmpdir / "bananas.l" / f"{banana['origin']}.yaml", "w+"
                ) as fh:
                    fh.write(yaml.dump(banana))
            with open(tmpdir / "stock.yaml", "w+") as fh:
                fh.write(yaml.dump(VALID_DB["stock"]))
            self.assertLoaderContent(DBSplittedFilesLoader(tmpdir))

    def test_load_path_not_found(self):
        with self.assertRaisesRegex(DBFormatError, "DB path /dev/fail does not exist"):
            DBSplittedFilesLoader(Path("/dev/fail"))

    def test_load_path_invalid_ext(self):
        with tempfile.TemporaryDirectory() as _tmpdir:
            tmpdir = Path(_tmpdir)
            with open(tmpdir / "pear.fail", "w+") as fh:
                fh.write(yaml.dump(VALID_DB["pear"]))
            with self.assertRaisesRegex(
                DBFormatError,
                r"^DB contains file .*pear.fail without valid extensions: .*$",
            ):
                DBSplittedFilesLoader(tmpdir)


class TestDBStdinLoader(TestDBLoaderBase):
    def test_load(self):
        with mock.patch("sys.stdin", new=io.StringIO(yaml.dump(VALID_DB))):
            self.assertLoaderContent(DBStdinLoader())

    def test_load_composer_error(self):
        with mock.patch("sys.stdin", new=io.StringIO(COMPOSER_ERROR_STR)):
            with self.assertRaisesRegex(DBFormatError, "^found undefined alias .*"):
                DBStdinLoader()


class TestDBStringLoader(TestDBLoaderBase):
    def test_load(self):
        DBStringLoader(yaml.dump(VALID_DB))

    def test_load_initial(self):
        db = VALID_DB.copy()
        del db["apples"]
        initial = {"apples": VALID_DB["apples"]}
        self.assertLoaderContent(DBStringLoader(yaml.dump(db), initial=initial))

    def test_load_composer_error(self):
        with self.assertRaisesRegex(DBFormatError, "^found undefined alias .*"):
            DBStringLoader(COMPOSER_ERROR_STR)
