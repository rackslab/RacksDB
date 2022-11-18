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
import logging

from .errors import DBSchemaError

logger = logging.getLogger(__name__)


class SchemaDefinedTypeLoader:
    def __init__(self, path):
        self.path = path

    @property
    def content(self):
        results = {}
        base_module = importlib.import_module(self.path)
        logger.debug("Searching module in %s", base_module.__path__)
        for importer, modname, _ in pkgutil.iter_modules(base_module.__path__):
            logger.debug("Loading module %s/%s", modname, importer)
            module = importlib.import_module(f"{self.path}.{modname}")
            class_suffix = modname.replace('_', ' ').title().replace(' ', '')
            class_name = f"SchemaDefinedType{class_suffix}"
            logger.debug("Loading class %s", class_name)
            results[modname] = getattr(module, class_name)()
        return results


class SchemaFileLoader:
    def __init__(self, path, extensions):
        self.path = path
        self.extensions = extensions

    @property
    def content(self):
        if not self.path.exists():
            raise DBSchemaError(f"Schema path {self.path} does not exist")
        with open(self.path) as fh:
            try:
                result = yaml.safe_load(fh)
            except yaml.composer.ComposerError as err:
                raise DBSchemaError(err)
        # load schema extensions
        result = self.load_extensions(result)
        return result

    def load_extensions(self, result):
        if not self.extensions.exists():
            logger.debug(
                "Schema extensions file %s not found, skipping extensions",
                self.extensions,
            )
            return result

        logger.debug("Loading schema extensions file %s", self.extensions)
        with open(self.extensions) as fh:
            try:
                extensions = yaml.safe_load(fh)
            except yaml.composer.ComposerError as err:
                raise DBSchemaError(err)
        if '_content' in extensions:
            logger.debug(
                "Updating schema with additional content found in extension"
            )
            result['_content'].update(extensions['_content'])
        if '_objects' in extensions:
            for obj, properties in extensions['_objects'].items():
                if obj in result['_objects']:
                    logger.debug(
                        "Updating object class %s with properties found in extension",
                        obj,
                    )
                    result['_objects'][obj].update(properties)
                else:
                    logger.debug(
                        "Additional object class %s found in extension", obj
                    )
                    result['_objects'][obj] = properties
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
        elif self.native is bool:
            return 'bool'


class SchemaObject(SchemaGenericValueType):
    def __init__(self, name):
        self.name = name
        self.properties = []  # list of SchemaProperty
        self.expandable = False
        # Set of SchemaObject attached to this object properties, recursively.
        self.subobjs = set()
        # Set of references in this object and sub-objects properties.
        self.refs = set()

    def __str__(self):
        if self.expandable:
            return f"Schema{self.name}+"
        else:
            return f"Schema{self.name}"

    def prop(self, name):
        for _prop in self.properties:
            if _prop.name == name:
                return _prop
        return None


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
    def __init__(self, obj, prop):
        self.obj = obj
        self.prop = prop

    def __str__(self):
        return f"${self.obj}.{self.prop}"


class SchemaBackReference(SchemaGenericValueType):
    def __init__(self, obj, prop):
        self.obj = obj
        self.prop = prop

    def __str__(self):
        result = f"^{self.obj}"
        if self.prop is not None:
            result += f".{self.prop}"
        return result


class SchemaProperty:
    def __init__(self, name, required, key, default, value_type):
        self.name = name
        self.required = required
        self.key = key
        self.default = default
        self.type = value_type

    def __str__(self):
        if self.required:
            result = 'required '
        else:
            result = 'optional '
        if self.key:
            result += 'key '
        result += str(self.type)
        if self.default is not None:
            result += f" ({self.default})"
        return result


class Schema:

    pattern_type_obj = re.compile(r":(\w+)")
    pattern_type_defined = re.compile(r"~(\w+)")
    pattern_type_ref = re.compile(r"\$(\w+)\.(\w+)")
    pattern_type_backref = re.compile(r"\^(\w+)(\.(\w+))?")
    pattern_type_list = re.compile(r"list\[(.+)\]")

    def __init__(self, schema_loader, types_loader):
        self._schema = schema_loader.content

        try:
            self.version = self._schema['_version']
        except KeyError:
            raise DBSchemaError("Version must be defined in schema")
        self.types = types_loader.content

        self.objects = {}

        try:
            self.content = self.parse_obj('_content', self._schema['_content'])
        except KeyError:
            raise DBSchemaError("Content must be defined in schema")

    def prop_spec(self, name, spec):
        # check optional
        required = True
        if spec.startswith('optional '):
            required = False
            spec = spec[9:]  # remove optional key

        # check key
        key = False
        if spec.startswith('key '):
            key = True
            spec = spec[4:]  # remove keyword

        # check default
        default = None
        if spec.startswith('default '):
            required = False
            items = spec.split(' ')
            # The default value is loaded using the yaml library to convert the
            # value to the appropriate Python type.
            default = yaml.safe_load(items[1])
            spec = items[2]
        return SchemaProperty(
            name, required, key, default, self.value_type(spec)
        )

    def value_type(self, spec):
        # parse native types
        for native_type in (str, int, float, bool):
            if spec == native_type.__name__:
                return SchemaNativeType(native_type)
        if spec == 'expandable':
            return SchemaExpandable()
        if spec == 'rangeid':
            return SchemaRangeId()
        # list
        match = self.pattern_type_list.match(spec)
        if match is not None:
            content = self.value_type(match.group(1))
            return SchemaContainerList(content)
        # obj
        match = self.pattern_type_obj.match(spec)
        if match is not None:
            return self.find_obj(match.group(1))
        # defined
        match = self.pattern_type_defined.match(spec)
        if match is not None:
            return self.find_defined_type(match.group(1))
        # ref
        match = self.pattern_type_ref.match(spec)
        if match is not None:
            return self.obj_reference(spec, match.group(1), match.group(2))
        # backref
        match = self.pattern_type_backref.match(spec)
        if match is not None:
            return self.obj_back_reference(match.group(1), match.group(3))
        raise DBSchemaError(f"Unable to parse value type '{spec}'")

    def find_obj(self, object_id):
        if object_id in self.objects:
            return self.objects[object_id]
        if (
            '_objects' not in self._schema
            or object_id not in self._schema['_objects']
        ):
            raise DBSchemaError(
                f"Definition of object {object_id} not found in schema"
            )
        obj = self.parse_obj(object_id, self._schema['_objects'][object_id])
        return obj

    def parse_obj(self, object_id, objdef):
        logger.debug("Loading class of %s", object_id)

        obj = SchemaObject(object_id)
        # The new SchemaObject must be added soon in objects hash to avoid
        # recursion loop in the following calls to prop_keys(), calling
        # value_type() → find_obj() → parse_obj() with back references.
        # There is an exception for _content fake root object as it is already
        # hold by Schema.content attribute.
        if object_id != '_content':
            self.objects[object_id] = obj

        has_key = False  # flag to check key property uniquess

        for key, spec in objdef.items():
            prop = self.prop_spec(key, spec)
            if isinstance(prop.type, SchemaObject) and prop.type.expandable:
                raise DBSchemaError(
                    f"Expandable object {prop.type} must be in a list, it "
                    f"cannot be member of object such as {object_id}"
                )
            if isinstance(prop.type, SchemaExpandable):
                # check expandable uniqueness
                if obj.expandable:
                    raise DBSchemaError(
                        f"Expandable object {object_id} cannot contain more "
                        "than one expandable property"
                    )
                obj.expandable = True
            if prop.key:
                # check key uniqueness among all properties
                if has_key:
                    raise DBSchemaError(
                        f"Object {object_id} cannot contain more than one key"
                    )
                has_key = True

            # Define refs and subobjs recursively
            if isinstance(prop.type, SchemaReference):
                obj.refs |= {prop.type.obj}
            subtype = prop.type
            if isinstance(prop.type, SchemaContainerList):
                subtype = prop.type.content
            if isinstance(subtype, SchemaObject):
                obj.refs |= subtype.refs
                obj.subobjs |= {subtype} | subtype.subobjs
            obj.properties.append(prop)
        logger.debug(
            "Class %s refs: %s subobjs: %s",
            object_id,
            [obj.name for obj in obj.refs],
            [obj.name for obj in obj.subobjs],
        )
        return obj

    def find_defined_type(self, defined):
        try:
            return self.types[defined]
        except KeyError:
            raise DBSchemaError(
                f"Definition of defined type {defined} not found"
            )

    def obj_reference(self, spec, object_id, object_prop):
        obj = self.find_obj(object_id)
        # verify property is defined for object
        if obj.prop(object_prop) is None:
            raise DBSchemaError(
                f"Reference {spec} to undefined {obj} object property"
            )
        return SchemaReference(obj, object_prop)

    def obj_back_reference(self, object_id, object_prop):
        logger.debug("Loading back reference to %s", object_id)
        obj = self.find_obj(object_id)
        return SchemaBackReference(obj, object_prop)
