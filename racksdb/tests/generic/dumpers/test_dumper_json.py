# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import json

from racksdb.generic.dumpers.json import DBDumperJSON

from ..lib.common import valid_db


class TestDBDumperJSON(unittest.TestCase):
    def test_dump_list(self):
        db = valid_db()
        dumper = DBDumperJSON()
        result = dumper.dump(db.apples)
        json.loads(result)

    def test_dump_folded(self):
        db = valid_db()
        dumper = DBDumperJSON()
        result = dumper.dump(db.stock)
        stock = json.loads(result)
        self.assertEqual(len(stock["content"]), 2)

    def test_dump_expanded(self):
        db = valid_db()
        dumper = DBDumperJSON(fold=False)
        result = dumper.dump(db.stock)
        stock = json.loads(result)
        self.assertEqual(len(stock["content"]), 20)

    def test_dump_recursion(self):
        db = valid_db()
        dumper = DBDumperJSON()
        # Check recursion error is raised
        with self.assertRaisesRegex(ValueError, "Circular reference detected"):
            dumper.dump(db.bananas)

    def test_dump_map_attribute(self):
        db = valid_db()
        dumper = DBDumperJSON(objects_map={"TestBananaOrigin": "origin"})
        result = dumper.dump(db.bananas)
        bananas = json.loads(result)
        self.assertEqual(bananas[0]["species"][0]["origin"], bananas[0]["origin"])

    def test_dump_map_none(self):
        db = valid_db()
        dumper = DBDumperJSON(objects_map={"TestBananaOrigin": None})
        result = dumper.dump(db.bananas)
        bananas = json.loads(result)
        self.assertNotIn("origin", bananas[0]["species"][0])
