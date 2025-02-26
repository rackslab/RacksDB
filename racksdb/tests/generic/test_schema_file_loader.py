# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import tempfile
from pathlib import Path

import yaml

from racksdb.generic.schema import SchemaFileLoader
from racksdb.generic.errors import DBSchemaError

from .lib.common import VALID_SCHEMA, VALID_EXTENSIONS


class TestSchemaFileLoader(unittest.TestCase):
    def test_ok(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            with open(tmpfile.name, "w+") as fh:
                fh.write(yaml.dump(VALID_SCHEMA))
            loader = SchemaFileLoader(Path(tmpfile.name))
            self.assertIsInstance(loader.content, dict)

    def test_file_not_found(self):
        loader = SchemaFileLoader(Path("/dev/fail"))
        with self.assertRaisesRegex(
            DBSchemaError, "Schema path /dev/fail does not exist"
        ):
            _ = loader.content

    def test_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_path = Path(tmpdir) / "schema.yaml"
            ext_path = Path(tmpdir) / "extensions.yaml"
            with open(schema_path, "w+") as fh:
                fh.write(yaml.dump(VALID_SCHEMA))
            with open(ext_path, "w+") as fh:
                fh.write(yaml.dump(VALID_EXTENSIONS))
            loader = SchemaFileLoader(schema_path, ext_path)
            content = loader.content
        self.assertIsInstance(content, dict)
        self.assertIn("plums", content["_content"]["properties"].keys())
        self.assertIn("juiciness", content["_objects"]["Pear"]["properties"].keys())
        self.assertIn("Plum", content["_objects"].keys())
