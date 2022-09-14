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
import importlib
import pkgutil
import yaml

from .errors import RacksDBSchemaError


class SchemaDefinedTypeLoader:
    def __init__(self, path):
        self.path = path

    @property
    def content(self):
        results = {}
        base_module = importlib.import_module(self.path)
        print(f"-> Searching module in {base_module.__path__}")
        for importer, modname, _ in pkgutil.iter_modules(base_module.__path__):
            print(f"-> Loading module {modname}/{importer}")
            module = importlib.import_module(f"{self.path}.{modname}")
            class_suffix = modname.replace('_', ' ').title().replace(' ', '')
            class_name = f"SchemaDefinedType{class_suffix}"
            print(f"-> Loading class {class_name}")
            results[modname] = getattr(module, class_name)()
        return results


class SchemaFileLoader:
    def __init__(self, path):
        self.path = path

    @property
    def content(self):
        with open(self.path) as fh:
            try:
                result = yaml.safe_load(fh)
            except yaml.composer.ComposerError as err:
                raise RacksDBSchemaError(err)
        return result


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


class SchemaExpandableObject(SchemaObject):
    def __str__(self):
        return f"Schema{self.name}+"


class SchemaContainerList(SchemaGenericValueType):
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return f"list[{self.content}]"


class SchemaExpandable(SchemaGenericValueType):
    def __str__(self):
        return f"expandable"


class SchemaRangeId(SchemaGenericValueType):
    def __str__(self):
        return f"rangeid"


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

    def __init__(self, schema_loader, types_loader):
        self._schema = schema_loader.content

        self.version = self._schema['_version']

        self.types = types_loader.content

        self.objects = {}

        self.content = self.parse_obj('_content', self._schema['_content'])

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
        elif spec == 'rangeid':
            return SchemaRangeId()
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
        if object_id not in self._schema['_objects']:
            raise RacksDBSchemaError(
                f"definition of object {object_id} not found"
            )
        obj = self.parse_obj(object_id, self._schema['_objects'][object_id])
        self.objects[object_id] = obj
        return obj

    def parse_obj(self, object_id, objdef):
        items = []
        expandable = False
        for key, spec in objdef.items():
            item = self.item_spec(key, spec)
            if isinstance(item.type, SchemaExpandableObject):
                raise RacksDBSchemaError(
                    f"expandable object {item.type} must be in a list, it cannot be member of object such as {object_id}"
                )
            if isinstance(item.type, SchemaExpandable):
                # check expandable uniqueness
                if expandable:
                    raise RacksDBSchemaError(
                        f"expandable object {object_id} cannot contain more than one expandable item"
                    )
                expandable = True
            items.append(item)
        if expandable:
            obj = SchemaExpandableObject(object_id, items)
        else:
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
            print(f"  {name}: {defined_type.pattern}")
        print("_objects:")
        for name, obj in self.objects.items():
            print(f"  {name}:")
            obj.dump(indent=4)
        print("_content:")
        self.content.dump(indent=2)
