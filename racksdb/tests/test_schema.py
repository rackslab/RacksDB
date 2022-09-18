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
import copy

from racksdb.generic.schema import Schema
from racksdb.generic.definedtype import SchemaDefinedType
from racksdb.generic.errors import DBSchemaError


class FakeSchemaLoader:
    def __init__(self, content):
        self.content = content


class FakeTypesLoader:
    def __init__(self, content):
        self.content = content


VALID_SCHEMA = {
    '_version': '1',
    '_content': {
        'apples': 'list[:Apple]',
        'pear': ':Pear',
        'bananas': 'optional list[:Banana]',
    },
    '_objects': {
        'Apple': {
            'color': 'str',
            'weight': '~weight',
            'variety': 'str',
        },
        'Pear': {'color': 'str', 'weight': '~weight', 'variety': 'str'},
        'Banana': {'origin': 'str'},
    },
}

VALID_DEFINED_TYPES = {'weight': SchemaDefinedType()}


class TestSchema(unittest.TestCase):
    def test_empty_schema(self):
        schema_loader = FakeSchemaLoader({})
        types_loader = FakeTypesLoader({})
        with self.assertRaisesRegex(
            DBSchemaError, 'Version must be defined in schema'
        ):
            Schema(schema_loader, types_loader)

    def test_empty_content(self):
        schema_loader = FakeSchemaLoader({'_version': '0'})
        types_loader = FakeTypesLoader({})
        with self.assertRaisesRegex(
            DBSchemaError, 'Content must be defined in schema'
        ):
            Schema(schema_loader, types_loader)

    def test_minimal_schema(self):
        schema_loader = FakeSchemaLoader({'_version': '0', '_content': {}})
        types_loader = FakeTypesLoader({})
        schema = Schema(schema_loader, types_loader)
        self.assertEqual(schema.version, '0')
        self.assertEqual(len(schema.types), 0)
        self.assertEqual(len(schema.content.properties), 0)

    def test_valid_schema(self):
        schema_loader = FakeSchemaLoader(VALID_SCHEMA)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        schema = Schema(schema_loader, types_loader)
        self.assertEqual(schema.version, '1')
        self.assertEqual(len(schema.types), 1)
        self.assertEqual(len(schema.content.properties), 3)

    def test_missing_objects(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        del schema_content['_objects']
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError, "Definition of object \w+ not found in schema"
        ):
            Schema(schema_loader, types_loader)

    def test_missing_object(self):
        for obj in VALID_SCHEMA['_objects'].keys():
            schema_content = copy.deepcopy(VALID_SCHEMA)
            del schema_content['_objects'][obj]
            schema_loader = FakeSchemaLoader(schema_content)
            types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
            with self.assertRaisesRegex(
                DBSchemaError, f"Definition of object {obj} not found in schema"
            ):
                Schema(schema_loader, types_loader)
