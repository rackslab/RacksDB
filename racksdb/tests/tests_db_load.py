# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from racksdb import RacksDB

from ..lib.common import schema_path, db_path


class TestDBLoad(unittest.TestCase):
    def setUp(self):
        try:
            self.schema_path = schema_path()
            self.db_path = db_path()
        except FileNotFoundError as err:
            self.skipTest(err)

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
