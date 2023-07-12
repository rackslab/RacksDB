#!/usr/bin/env python3
#
# Copyright (C) 2022 Rackslab
#
# This file is part of RacksDB.
#
# RacksDB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RacksDB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RacksDB.  If not, see <https://www.gnu.org/licenses/>.

import unittest

from racksdb.generic.schema import SchemaDefinedTypeLoader
from racksdb.generic.definedtype import SchemaDefinedType


class TestSchemaDefinedTypeLoader(unittest.TestCase):
    def test_schema_defined_type_loader(self):
        # Load defined types provided in RacksDB
        loader = SchemaDefinedTypeLoader('racksdb.dtypes')
        # Verify at least one defined type has been loaded
        self.assertGreater(len(loader.content), 0)
        # Verify loader content is a dict
        self.assertIs(type(loader.content), dict)
        # Verify content values are valid SchemaDefinedType
        for defined_type in loader.content.values():
            self.assertIsInstance(defined_type, SchemaDefinedType)
