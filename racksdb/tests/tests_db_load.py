# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from pathlib import Path
import unittest

from racksdb import RacksDB


class TestDBLoad(unittest.TestCase):
    def setUp(self):
        # Try relative path and system paths sequentially for both the schema
        # and example database. If none of these paths exist, gently skip the
        # test with meaningful message.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        schema_paths = [
            Path(current_dir).joinpath("../../schema/racksdb.yml"),
            Path("/usr/share/racksdb/schema.yml"),
        ]
        self.schema_path = None
        for schema_path in schema_paths:
            if schema_path.exists():
                self.schema_path = schema_path
                break
        if self.schema_path is None:
            self.skipTest("Unable to find schema file to run test")
        db_paths = [
            Path(current_dir).joinpath("../../examples/db"),
            Path("/usr/share/doc/racksdb/examples/db"),
        ]
        self.db_path = None
        for db_path in db_paths:
            if db_path.exists():
                self.db_path = db_path
                break
        if self.db_path is None:
            self.skipTest("Unable to find db file to run test")

    def test_load(self):
        RacksDB.load(schema=self.schema_path, db=self.db_path)

    def test_content(self):
        db = RacksDB.load(schema=self.schema_path, db=self.db_path)
        self.assertEqual(type(db), RacksDB)
        self.assertEqual(len(db.infrastructures), 3)
        # Thanks to lazy loading, just a few expandable object are loaded, much
        # fewer than the number of nodes. The number of potentially expanded
        # objects is reported correctly by len(). However, it must be much lower
        # than the actual number of keys/values in the dictionnary.
        self.assertEqual(len(db.nodes.keys()), 6)
        self.assertEqual(len(db.nodes), 129)
        self.assertEqual(
            type(db.infrastructures.first()).__name__, "RacksDBInfrastructure"
        )
        self.assertEqual(db.infrastructures["mercury"].name, "mercury")
        self.assertEqual(len(db.infrastructures["mercury"].nodes.keys()), 6)
        self.assertEqual(len(db.infrastructures["mercury"].nodes), 129)
        self.assertEqual(len(db.infrastructures["mercury"].layout[0].nodes), 61)
        self.assertEqual(
            type(db.infrastructures["mercury"].nodes["mecn0001"]).__name__,
            "RacksDBNode",
        )
        self.assertEqual(
            db.infrastructures["mercury"].nodes["mecn0001"].name, "mecn0001"
        )
        self.assertEqual(
            db.infrastructures["mercury"].nodes["mecn0001"].type.model,
            "SuperMicro A+ Server 2124BT-HTR",
        )
        self.assertEqual(
            db.infrastructures["mercury"].nodes["mecn0010"]._first.name, "mecn0001"
        )
        self.assertEqual(
            db.infrastructures["mercury"].nodes["mecn0010"].tags, ["compute"]
        )
        node = db.infrastructures["mercury"].nodes["mecn0001"]
        self.assertEqual(node, node._first)
        # print(db.infrastructures["mercury"].nodes)
