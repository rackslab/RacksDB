# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from racksdb import RacksDB

from .lib.common import schema_path, db_path


class TestDB(unittest.TestCase):
    def setUp(self):
        try:
            self.schema_path = schema_path()
            self.db_path = db_path()
        except FileNotFoundError as err:
            self.skipTest(err)
        self.db = RacksDB.load(schema=self.schema_path, db=self.db_path)

    def test_content(self):
        self.assertIsInstance(self.db, RacksDB)
        self.assertEqual(len(self.db.infrastructures), 3)
        self.assertEqual(
            type(self.db.infrastructures.first()).__name__, "RacksDBInfrastructure"
        )
        self.assertEqual(self.db.infrastructures["mercury"].name, "mercury")
        self.assertEqual(len(self.db.infrastructures["mercury"].nodes.keys()), 6)
        self.assertEqual(len(self.db.infrastructures["mercury"].nodes), 129)
        self.assertEqual(len(self.db.infrastructures["mercury"].layout[0].nodes), 61)
        self.assertEqual(
            type(self.db.infrastructures["mercury"].nodes["mecn0001"]).__name__,
            "RacksDBNode",
        )
        self.assertEqual(
            self.db.infrastructures["mercury"].nodes["mecn0001"].name, "mecn0001"
        )
        self.assertEqual(
            self.db.infrastructures["mercury"].nodes["mecn0001"].type.model,
            "SuperMicro A+ Server 2124BT-HTR",
        )
        self.assertEqual(
            self.db.infrastructures["mercury"].nodes["mecn0010"]._first.name, "mecn0001"
        )
        self.assertEqual(
            self.db.infrastructures["mercury"].nodes["mecn0010"].tags, ["compute"]
        )
        node = self.db.infrastructures["mercury"].nodes["mecn0001"]
        self.assertEqual(node, node._first)

    def test_nodes(self):
        # Thanks to lazy loading, just a few expandable object are loaded, much
        # fewer than the number of nodes. The number of potentially expanded
        # objects is reported correctly by len(). However, it must be much lower
        # than the actual number of keys/values in the dictionnary.
        self.assertEqual(len(self.db.nodes.keys()), 7)
        self.assertEqual(len(self.db.nodes), 130)

    def test_racks(self):
        self.assertEqual(len(self.db.racks), 101)
        self.assertEqual(
            self.db.racks[0].name,
            self.db.datacenters.first()
            .rooms.first()
            .rows.first()
            .racks[0]
            .objects()[0]
            .name,
        )
