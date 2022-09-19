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
        'stock': 'list[:AppleCrate]',
    },
    '_objects': {
        'Apple': {
            'color': 'str',
            'weight': '~weight',
            'variety': 'str',
        },
        'Pear': {'color': 'str', 'weight': '~weight', 'variety': 'str'},
        'Banana': {'origin': 'str'},
        'AppleCrate': {
            'name': 'expandable',
            'id': 'rangeid',
            'variety': '$Apple.variety',
            'quantity': 'int',
        },
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
        self.assertEqual(len(schema.content.properties), 4)

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

    def test_missing_defined_type(self):
        schema_loader = FakeSchemaLoader(VALID_SCHEMA)
        defined_types = copy.deepcopy(VALID_DEFINED_TYPES)
        del defined_types['weight']
        types_loader = FakeTypesLoader(defined_types)
        with self.assertRaisesRegex(
            DBSchemaError, "Definition of defined type weight not found"
        ):
            Schema(schema_loader, types_loader)

    def test_invalid_type(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content['_objects']['Apple']['color'] = 'fail'
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError, "Unable to parse value type 'fail'"
        ):
            Schema(schema_loader, types_loader)

    def test_expandable_not_in_list(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content['_content']['stock'] = ':AppleCrate'
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError,
            "Expandable object SchemaAppleCrate\+ must be in a list, it cannot "
            "be member of object such as _content",
        ):
            Schema(schema_loader, types_loader)

    def test_expandable_double(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content['_objects']['AppleCrate']['quantity'] = 'expandable'
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError,
            "Expandable object AppleCrate cannot contain more than one "
            "expandable property",
        ):
            Schema(schema_loader, types_loader)

    def test_reference_undefined_object(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content['_objects']['AppleCrate']['variety'] = '$Unknown.object'
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError,
            "Definition of object Unknown not found in schema",
        ):
            Schema(schema_loader, types_loader)

    def test_reference_undefined_property(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content['_objects']['AppleCrate']['variety'] = '$Apple.unknown'
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError,
            "Reference \$Apple.unknown to undefined SchemaApple object "
            "property",
        ):
            Schema(schema_loader, types_loader)
