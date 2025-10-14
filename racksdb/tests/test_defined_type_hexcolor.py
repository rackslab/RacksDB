# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import unittest

from racksdb.drawers.dtypes.hexcolor import SchemaDefinedTypeHexcolor
from racksdb.generic.errors import DBFormatError


class TestDefinedTypeHexcolor(unittest.TestCase):
    def test_defined_type_hexcolor(self):
        defined_type = SchemaDefinedTypeHexcolor()
        self.assertEqual(defined_type.parse("#004080"), (0, 64 / 255, 128 / 255, 1.0))
        self.assertEqual(
            defined_type.parse("#ffb4c5"), (1.0, 180 / 255, 197 / 255, 1.0)
        )

    def test_defined_type_hexcolor_invalid_values(self):
        defined_type = SchemaDefinedTypeHexcolor()
        for value in ["001122", "fail"]:
            with self.assertRaises(DBFormatError):
                defined_type.parse(value)
