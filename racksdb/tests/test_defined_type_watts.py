# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from racksdb.dtypes.watts import SchemaDefinedTypeWatts
from racksdb.generic.errors import DBFormatError


class TestDefinedTypeWatts(unittest.TestCase):
    def test_defined_type_watts(self):
        defined_type = SchemaDefinedTypeWatts()
        self.assertEqual(defined_type.parse("15W"), 15)
        self.assertEqual(defined_type.parse("100.4kW"), 100.4 * 10**3)
        self.assertEqual(defined_type.parse("3.4MW"), 3.4 * 10**6)
        self.assertEqual(defined_type.parse("1.1W"), 1)  # rounded to integer below

    def test_defined_type_watts_invalid_values(self):
        defined_type = SchemaDefinedTypeWatts()
        for value in ["1", "1.4.3W", "3.4K"]:
            with self.assertRaises(DBFormatError):
                defined_type.parse(value)
