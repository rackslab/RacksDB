# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

import yaml

from racksdb.generic.dumpers.yaml import DBDumperYAML, SchemaDumperYAML

from ..lib.common import valid_db, valid_schema


class TestDBDumperYAML(unittest.TestCase):
    def test_dump_list(self):
        db = valid_db()
        dumper = DBDumperYAML()
        result = dumper.dump(db.apples)
        yaml.safe_load(result)

    def test_dump_show_types(self):
        db = valid_db()
        dumper = DBDumperYAML(show_types=True)
        dumper.dump(db.apples)

    def test_dump_folded(self):
        db = valid_db()
        dumper = DBDumperYAML()
        result = dumper.dump(db.stock)
        stock = yaml.safe_load(result)
        self.assertEqual(len(stock["content"]), 2)

    def test_dump_expanded(self):
        db = valid_db()
        dumper = DBDumperYAML(fold=False)
        result = dumper.dump(db.stock)
        stock = yaml.safe_load(result)
        self.assertEqual(len(stock["content"]), 20)

    def test_dump_recursion(self):
        db = valid_db()
        dumper = DBDumperYAML()
        with self.assertLogs("racksdb", "ERROR") as cm:
            result = dumper.dump(db.bananas)
        # Check one error has been logged and check its value.
        self.assertEqual(len(cm.output), 1)
        self.assertIn(
            "ERROR:racksdb.generic.dumpers.yaml:Recursion loop detected during dump, "
            "last represented objects:",
            cm.output[0],
        )
        self.assertEqual(result, "")

    def test_dump_map_attribute(self):
        db = valid_db()
        dumper = DBDumperYAML(objects_map={"TestBananaOrigin": "origin"})
        result = dumper.dump(db.bananas)
        bananas = yaml.safe_load(result)
        self.assertEqual(bananas[0]["species"][0]["origin"], bananas[0]["origin"])

    def test_dump_map_none(self):
        db = valid_db()
        dumper = DBDumperYAML(objects_map={"TestBananaOrigin": None})
        result = dumper.dump(db.bananas)
        bananas = yaml.safe_load(result)
        self.assertNotIn("origin", bananas[0]["species"][0])


class TestSchemaDumperYAML(unittest.TestCase):
    def test_dump(self):
        result = SchemaDumperYAML().dump(valid_schema())
        yaml.safe_load(result)
