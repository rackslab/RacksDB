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

import re

import yaml

from .errors import RacksDBSchemaError


class SchemaGenericValueType:
    pass


class SchemaNativeType(SchemaGenericValueType):
    def __init__(self, native):
        self.native = native

    def __str__(self):
        if self.native is str:
            return 'str'
        elif self.native is int:
            return 'int'
        elif self.native is float:
            return 'float'


class SchemaDefinedType(SchemaGenericValueType):
    def __init__(self, name, regex):
        self.name = name
        self.regex = regex

    def __str__(self):
        return f"~{self.name}"


class SchemaObject(SchemaGenericValueType):
    def __init__(self, name, items):
        self.name = name
        self.items = items  # list of SchemaItemSpec

    def __str__(self):
        return f"Schema{self.name}"

    def dump(self, indent):
        for item in self.items:
            print(f"{' '*indent}{item.name}: {item.type}")

    def item(self, name):
        for item in self.items:
            if item.name == name:
                return item
        return None


class SchemaContainerList(SchemaGenericValueType):
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return f"list[{self.content}]"


class SchemaExpandable(SchemaGenericValueType):
    def __str__(self):
        return f"expandable"


class SchemaReference(SchemaGenericValueType):
    def __init__(self, obj, attribute):
        self.obj = obj
        self.attribute = attribute

    def __str__(self):
        return f"${self.obj}.{self.attribute}"


class SchemaItemSpec:
    def __init__(self, name, required, value_type):
        self.name = name
        self.required = required
        self.type = value_type

    def __str__(self):
        if self.required:
            return f"required {self.type}"
        else:
            return f"optional {self.type}"


class Schema:

    pattern_type_obj = re.compile(r":(\w+)")
    pattern_type_custom = re.compile(r"~(\w+)")
    pattern_type_ref = re.compile(r"\$(\w+)\.(\w+)")
    pattern_type_list = re.compile(r"list\[(.+)\]")

    def __init__(self, db):
        self.db = db

        self.version = db['_version']

        self.types = {}
        for key, spec in db['_types'].items():
            self.types[key] = SchemaDefinedType(key, spec)

        self.objects = {}

        self.content = self.parse_obj('_content', db['_content'])

    def item_spec(self, name, spec):
        # check optional
        required = True
        if spec.startswith('optional '):
            required = False
            spec = spec[9:]  # remove optional key

        return SchemaItemSpec(name, required, self.value_type(spec))

    def value_type(self, spec):
        # parse native types
        if spec == 'str':
            return SchemaNativeType(str)
        elif spec == 'int':
            return SchemaNativeType(int)
        elif spec == 'float':
            return SchemaNativeType(float)
        elif spec == 'expandable':
            return SchemaExpandable()
        else:
            # list
            match = self.pattern_type_list.match(spec)
            if match is not None:
                content = self.value_type(match.group(1))
                return SchemaContainerList(content)
            # obj
            match = self.pattern_type_obj.match(spec)
            if match is not None:
                return self.find_obj(match.group(1))
            # custom
            match = self.pattern_type_custom.match(spec)
            if match is not None:
                return self.find_defined_type(match.group(1))
            # ref
            match = self.pattern_type_ref.match(spec)
            if match is not None:
                obj = self.find_obj(match.group(1))
                attribute = match.group(2)
                return SchemaReference(obj, attribute)
        raise RacksDBSchemaError(f"unable to parse value type '{spec}'")

    def find_obj(self, object_id):
        if object_id in self.objects:
            return self.objects[object_id]
        if object_id not in self.db['_objects']:
            raise RacksDBSchemaError(
                f"definition of object {object_id} not found"
            )
        obj = self.parse_obj(object_id, self.db['_objects'][object_id])
        self.objects[object_id] = obj
        return obj

    def parse_obj(self, object_id, objdef):
        items = []
        for key, spec in objdef.items():
            items.append(self.item_spec(key, spec))
        obj = SchemaObject(object_id, items)
        return obj

    def find_defined_type(self, custom):
        try:
            return self.types[custom]
        except KeyError:
            raise RacksDBSchemaError(
                f"definition of defined type {custom} not found"
            )

    def dump(self):
        print("_types:")
        for name, defined_type in self.types.items():
            print(f"  {name}: {defined_type.regex}")
        print("_objects:")
        for name, obj in self.objects.items():
            print(f"  {name}:")
            obj.dump(indent=4)
        print("_content:")
        self.content.dump(indent=2)

    @classmethod
    def load(cls, path):
        with open(path) as fh:
            try:
                db = yaml.safe_load(fh)
            except yaml.composer.ComposerError as err:
                raise RacksDBSchemaError(err)
        return cls(db)
