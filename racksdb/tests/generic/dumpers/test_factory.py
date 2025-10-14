# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import unittest

from racksdb.generic.dumpers import DBDumperFactory, SchemaDumperFactory
from racksdb.generic.dumpers.json import DBDumperJSON
from racksdb.generic.dumpers.yaml import DBDumperYAML, SchemaDumperYAML
from racksdb.generic.dumpers.console import DBDumperConsole
from racksdb.generic.errors import DBDumperError


class TestDBDumperFactory(unittest.TestCase):
    def test_get(self):
        self.assertIs(DBDumperFactory.get("json"), DBDumperJSON)
        self.assertIs(DBDumperFactory.get("yaml"), DBDumperYAML)
        self.assertIs(DBDumperFactory.get("console"), DBDumperConsole)

    def test_get_fail(self):
        with self.assertRaisesRegex(DBDumperError, "Unsupported DB dump format fail"):
            DBDumperFactory.get("fail")


class TestSchemaDumperFactor(unittest.TestCase):
    def test_get(self):
        self.assertIs(SchemaDumperFactory.get("yaml"), SchemaDumperYAML)

    def test_get_fail(self):
        with self.assertRaisesRegex(
            DBDumperError, "Unsupported schema dump format fail"
        ):
            SchemaDumperFactory.get("fail")
