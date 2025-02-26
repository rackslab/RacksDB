# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from racksdb.generic.views import DBView, DBAction
from racksdb.generic.errors import DBViewError

from .lib.views import TestDBViews


class TestDBViewSet(unittest.TestCase):

    def setUp(self):
        self.views = TestDBViews()

    def test_iter(self):
        for view in self.views:
            self.assertIsInstance(view, DBView)

    def test_views_actions(self):
        actions = self.views.views_actions()
        self.assertIsInstance(actions, list)
        for action in actions:
            self.assertIsInstance(action, DBAction)

    def test_actions(self):
        for action in self.views.actions():
            self.assertIsInstance(action, DBAction)

    def test_getitem(self):
        _ = self.views["apples"]

    def test_getitem_not_found(self):
        with self.assertRaisesRegex(
            DBViewError, "^Unable to find view for 'fail' content$"
        ):
            _ = self.views["fail"]
