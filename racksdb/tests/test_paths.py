# Copyright (c) 2026 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import sys
import unittest
from pathlib import Path
from unittest import mock

from racksdb import RacksDB
from racksdb.drawers.parameters import DrawingParameters
from racksdb.paths import _SOURCE_TREE_SCHEMAS, schema_file


class TestSchemaFile(unittest.TestCase):
    FHS = Path("/usr/share/racksdb/schemas/racksdb.yml")

    def test_prefers_existing_fhs_path(self):
        with mock.patch.object(Path, "is_file", return_value=True):
            result = schema_file("racksdb.yml")
        self.assertEqual(result, self.FHS)

    def test_uses_pip_data_when_fhs_missing(self):
        pip_path = Path(sys.prefix) / "share" / "racksdb" / "schemas" / "racksdb.yml"

        def is_file(self):
            return self == pip_path

        with mock.patch.object(Path, "is_file", is_file):
            result = schema_file("racksdb.yml")
        self.assertEqual(result, pip_path)

    def test_uses_source_tree_when_fhs_and_pip_missing(self):
        dev_path = _SOURCE_TREE_SCHEMAS / "racksdb.yml"

        def is_file(self):
            return self == dev_path

        with mock.patch.object(Path, "is_file", is_file):
            result = schema_file("racksdb.yml")
        self.assertEqual(result, dev_path)

    def test_returns_fhs_path_when_nothing_found(self):
        with mock.patch.object(Path, "is_file", return_value=False):
            result = schema_file("racksdb.yml")
        self.assertEqual(result, self.FHS)


class TestDefaultSchemaPaths(unittest.TestCase):
    def test_racksdb_default_schema_exists(self):
        self.assertTrue(Path(RacksDB.DEFAULT_SCHEMA).is_file())

    def test_drawing_parameters_default_schema_exists(self):
        self.assertTrue(Path(DrawingParameters.DEFAULT_SCHEMA).is_file())
