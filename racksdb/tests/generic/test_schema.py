# Copyright (c) 2022-2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import copy

from racksdb.generic.schema import Schema
from racksdb.generic.errors import DBSchemaError

from .lib.common import (
    FakeSchemaLoader,
    FakeTypesLoader,
    VALID_SCHEMA,
    VALID_DEFINED_TYPES,
    valid_schema,
)


class TestSchema(unittest.TestCase):
    def test_empty_schema(self):
        schema_loader = FakeSchemaLoader({})
        types_loader = FakeTypesLoader({})
        with self.assertRaisesRegex(DBSchemaError, "Version must be defined in schema"):
            Schema(schema_loader, types_loader)

    def test_empty_content(self):
        schema_loader = FakeSchemaLoader({"_version": "0"})
        types_loader = FakeTypesLoader({})
        with self.assertRaisesRegex(DBSchemaError, "Content must be defined in schema"):
            Schema(schema_loader, types_loader)

    def test_minimal_schema(self):
        schema_loader = FakeSchemaLoader(
            {"_version": "0", "_content": {"properties": {}}}
        )
        types_loader = FakeTypesLoader({})
        schema = Schema(schema_loader, types_loader)
        self.assertEqual(schema.version, "0")
        self.assertEqual(len(schema.types), 0)
        self.assertEqual(len(schema.content.properties), 0)

    def test_valid_schema(self):
        schema = valid_schema()
        self.assertEqual(schema.version, "1")
        self.assertEqual(len(schema.types), 1)
        self.assertEqual(len(schema.content.properties), 4)

    def test_missing_objects(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        del schema_content["_objects"]
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError, r"Definition of object \w+ not found in schema"
        ):
            Schema(schema_loader, types_loader)

    def test_missing_object(self):
        for obj in VALID_SCHEMA["_objects"].keys():
            schema_content = copy.deepcopy(VALID_SCHEMA)
            del schema_content["_objects"][obj]
            schema_loader = FakeSchemaLoader(schema_content)
            types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
            with self.assertRaisesRegex(
                DBSchemaError, f"Definition of object {obj} not found in schema"
            ):
                Schema(schema_loader, types_loader)

    def test_missing_defined_type(self):
        schema_loader = FakeSchemaLoader(VALID_SCHEMA)
        defined_types = copy.deepcopy(VALID_DEFINED_TYPES)
        del defined_types["weight"]
        types_loader = FakeTypesLoader(defined_types)
        with self.assertRaisesRegex(
            DBSchemaError, "Definition of defined type weight not found"
        ):
            Schema(schema_loader, types_loader)

    def test_invalid_type(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content["_objects"]["Apple"]["properties"]["color"]["type"] = "fail"
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(DBSchemaError, "Unable to parse value type 'fail'"):
            Schema(schema_loader, types_loader)

    def test_multiple_keys(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        # BananaSpecies.name is already a key, try setting another property as key as
        # well.
        schema_content["_objects"]["Banana"]["properties"]["color"]["key"] = True
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError, "Object Banana cannot contain more than one key"
        ):
            Schema(schema_loader, types_loader)

    def test_expandable_not_in_list(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content["_content"]["properties"]["stock"]["type"] = ":AppleCrate"
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError,
            r"Expandable object SchemaAppleCrate\+ must be in a list, it cannot be "
            "member of object such as _content",
        ):
            Schema(schema_loader, types_loader)

    def test_expandable_double(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content["_objects"]["AppleCrate"]["properties"]["quantity"]["type"] = (
            "expandable"
        )
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError,
            "Expandable object AppleCrate cannot contain more than one expandable "
            "property",
        ):
            Schema(schema_loader, types_loader)

    def test_reference_undefined_object(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content["_objects"]["AppleCrate"]["properties"]["species"]["type"] = (
            "$Unknown.object"
        )
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError,
            "Definition of object Unknown not found in schema",
        ):
            Schema(schema_loader, types_loader)

    def test_reference_undefined_property(self):
        schema_content = copy.deepcopy(VALID_SCHEMA)
        schema_content["_objects"]["AppleCrate"]["properties"]["species"]["type"] = (
            "$Apple.unknown"
        )
        schema_loader = FakeSchemaLoader(schema_content)
        types_loader = FakeTypesLoader(VALID_DEFINED_TYPES)
        with self.assertRaisesRegex(
            DBSchemaError,
            r"Reference \$Apple.unknown to undefined SchemaApple object property",
        ):
            Schema(schema_loader, types_loader)

    def test_str_properties(self):
        schema = valid_schema()

        def get_object_property(obj, prop):
            if obj == "_content":
                _obj = schema.content
            else:
                _obj = schema.objects[obj]
            for _prop in _obj.properties:
                if _prop.name == prop:
                    return _prop

        # basic test
        self.assertEqual(str(get_object_property("Apple", "color")), "required str")
        # test key
        self.assertEqual(str(get_object_property("Banana", "name")), "required key str")
        # test default value
        self.assertEqual(
            str(get_object_property("Pear", "color")), "optional str (yellow)"
        )
        # test computed
        self.assertEqual(
            str(get_object_property("AppleStock", "total")), "computed int"
        )
        # test optional (without default value)
        self.assertEqual(
            str(get_object_property("_content", "bananas")),
            "optional list[SchemaBananaOrigin]",
        )
