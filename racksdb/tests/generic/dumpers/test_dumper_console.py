# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import unittest

from racksdb.generic.dumpers.console import DBDumperConsole
from racksdb.generic.db import DBList, DBDict
from racksdb.generic.errors import DBDumperError


class TestDBDumperConsole(unittest.TestCase):
    def test_dump(self):
        dumper = DBDumperConsole()
        # DBDumperConsole only support lists
        content = DBList()
        content.append("foo")
        content.append("bar")
        result = dumper.dump(content)
        self.assertEqual(result, "bar,foo")

    def test_dump_unsupported(self):
        dumper = DBDumperConsole()
        content = DBDict()
        content["foo"] = "bar"
        with self.assertRaisesRegex(
            DBDumperError,
            "Unsupported type '<class 'racksdb.generic.db.DBDict'>' for "
            "DBDumperConsole",
        ):
            dumper.dump(content)

    def test_dump_fold(self):
        dumper = DBDumperConsole()
        content = DBList()
        content.append("foo1")
        content.append("foo2")
        result = dumper.dump(content)
        self.assertEqual(result, "foo[1-2]")

    def test_dump_expand(self):
        dumper = DBDumperConsole(fold=False)
        content = DBList()
        content.append("foo1")
        content.append("foo2")
        result = dumper.dump(content)
        self.assertEqual(result, "foo1\nfoo2")
