# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from racksdb.generic.db import DBList

from .lib.common import valid_db


class TestDBList(unittest.TestCase):

    def setUp(self):
        self.db = valid_db()
        self.assertIsInstance(self.db.stock.content, DBList)

    def test_iter(self):
        nb = 0
        for item in self.db.stock.content:
            nb += 1
        self.assertEqual(nb, 20)

    def test_len(self):
        self.assertEqual(len(self.db.stock.content), 20)

    def test_itervalues(self):
        nb = 0
        for item in self.db.stock.content.itervalues():
            nb += 1
        self.assertEqual(nb, 2)

    def test_filter(self):
        selected = self.db.stock.content.filter(quantity_min=15)
        self.assertIsInstance(selected, DBList)
        self.assertEqual(len(selected), 10)
        selected = self.db.stock.content.filter(quantity_min=5)
        self.assertEqual(len(selected), 20)
