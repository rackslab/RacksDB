# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from racksdb.generic.db import DBDict, DBObjectRange, DBExpandableObject

from .lib.common import valid_db


class TestDBDict(unittest.TestCase):
    def setUp(self):
        self.db = valid_db()

    def test_filter_ok(self):
        self.assertIsInstance(self.db.apples, DBDict)
        yellow_species = self.db.apples.filter(color="yellow")
        self.assertIsInstance(yellow_species, DBDict)
        self.assertCountEqual(yellow_species.keys(), ["golden"])
        self.assertEqual(yellow_species["golden"].__class__.__name__, "TestApple")

    def test_filter_no_value(self):
        blue_species = self.db.apples.filter(color="blue")
        self.assertIsInstance(blue_species, DBDict)
        self.assertCountEqual(blue_species.keys(), [])

    def test_filter_invalid_criteria(self):
        with self.assertRaises(TypeError):
            self.db.apples.filter(fail="fail")

    def test_iter(self):
        nb = 0
        for item in self.db.apples:
            nb += 1
        self.assertEqual(nb, 2)

    def test_getitem(self):
        self.assertEqual(self.db.apples["golden"].__class__.__name__, "TestApple")

    def test_getitem_not_found(self):
        with self.assertRaisesRegex(KeyError, "fail"):
            self.db.apples["fail"]

    def test_len(self):
        self.assertEqual(len(self.db.apples), 2)

    def test_first(self):
        first = self.db.apples.first()
        self.assertEqual(first.__class__.__name__, "TestApple")


class TestDBDictExpandable(unittest.TestCase):
    def setUp(self):
        self.db = valid_db()
        self.expandable_dict = DBDict()
        # Create DBDict of DBExpandableObjects with DBList of AppleCrate.
        for crates in self.db.stock.content.itervalues():
            self.expandable_dict[crates.name] = crates
            self.assertIsInstance(crates.name, DBObjectRange)
            self.assertIsInstance(crates, DBExpandableObject)

    def test_expandable_filter(self):
        selected = self.expandable_dict.filter(quantity_min=15)
        self.assertIsInstance(selected, DBDict)
        self.assertEqual(len(selected), 10)
        selected = self.expandable_dict.filter(quantity_min=5)
        self.assertEqual(len(selected), 20)

    def test_expandable_iter(self):
        nb = 0
        for item in self.expandable_dict:
            nb += 1
        self.assertEqual(nb, 20)

    def test_expandable_getitem(self):
        self.assertEqual(self.expandable_dict["crate02"].name, "crate02")

    def test_expandable_len(self):
        self.assertEqual(len(self.expandable_dict), 20)

    def test_expandable_first(self):
        self.assertEqual(self.expandable_dict.first().name, "crate01")
