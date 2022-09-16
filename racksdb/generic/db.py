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
from typing import Union


import yaml
from ClusterShell.NodeSet import NodeSet

from .errors import DBFormatError
from .definedtype import SchemaDefinedType
from .schema import (
    SchemaNativeType,
    SchemaContainerList,
    SchemaExpandable,
    SchemaRangeId,
    SchemaObject,
    SchemaExpandableObject,
    SchemaReference,
    SchemaProperty,
)


class DBObject:
    def __init__(self, db, schema):
        self._db = db
        self._schema = schema

    def dump(self, indent):
        for attribute, value in vars(self).items():
            if attribute in ['_db']:
                continue
            if isinstance(value, list):
                print(f"{' '*indent}{attribute}:")
                for item in value:
                    if isinstance(item, DBExpandableObject):
                        for generated_obj in item.objects():
                            print(f"{' '*indent}-")
                            generated_obj.dump(indent + 2)
                    elif isinstance(item, DBObject):
                        print(f"{' '*indent}-")
                        item.dump(indent + 2)
                    else:
                        print(f"{' '*indent}- {item}")
            elif isinstance(value, DBObject):
                print(f"{' '*indent}{attribute}:")
                value.dump(indent + 2)
            else:
                print(f"{' '*indent}{attribute}: {value}")


class DBExpandableObject(DBObject):
    def objects(self):
        result = []
        stable_attributes = {}
        range_attribute = None
        rangeid_attributes = {}
        for attribute, value in vars(self).items():
            if isinstance(value, DBObjectRange):
                range_attribute = (attribute, value)
            elif isinstance(value, DBObjectRangeId):
                rangeid_attributes[attribute] = value
            else:
                stable_attributes[attribute] = value

        for index, value in enumerate(range_attribute[1].expanded()):
            _attributes = stable_attributes.copy()
            _attributes[range_attribute[0]] = value
            for rangeid_name, rangeid_value in rangeid_attributes.items():
                _attributes[rangeid_name] = rangeid_value.index(index)
            obj = type(
                f"{self._db._prefix}{self._schema.name}", (DBObject,), dict()
            )(self._db, self._schema)
            for attr_name, attr_value in _attributes.items():
                setattr(obj, attr_name, attr_value)
            result.append(obj)
        return result


class DBObjectRange:
    def __init__(self, rangeset):
        self.rangeset = NodeSet(rangeset)

    def expanded(self):
        return list(self.rangeset)


class DBObjectRangeId:
    def __init__(self, start):
        self.start = start

    def index(self, value):
        return self.start + value


class DBFileLoader:
    def __init__(self, path):
        with open(path) as fh:
            try:
                self.content = yaml.safe_load(fh)
            except yaml.composer.ComposerError as err:
                raise DBFormatError(err)


class GenericDB(DBObject):
    def __init__(self, prefix, schema):
        super().__init__(self, schema)
        self._prefix = prefix
        self._indexes = {}  # objects indexes

    def load(self, loader):
        for token, literal in loader.content.items():
            schema_item = self._schema.content.prop(token)
            if schema_item is None:
                raise DBFormatError(
                    f"key {key} is not defined in schema {schema_object.name}"
                )
            attribute = self.load_type(token, literal, schema_item.type)
            setattr(self, token, attribute)

    def load_type(
        self,
        token,
        literal,
        schema_arg: Union[SchemaProperty, SchemaNativeType],
    ):
        if isinstance(schema_arg, SchemaProperty):
            schema_type = schema_arg.type
        else:
            schema_type = schema_arg
        print(f"Loading item {token} ({schema_type})")
        if isinstance(schema_type, SchemaNativeType):
            if schema_type.native is str:
                if type(literal) != str:
                    DBFormatError(
                        f"token {token} of {schema_type} is not a valid str"
                    )
                return literal
            elif schema_type.native is int:
                if type(literal) != int:
                    DBFormatError(
                        f"token {token} of {schema_type} is not a valid int"
                    )
                return literal
            elif schema_type.native is float:
                if type(literal) != float:
                    DBFormatError(
                        f"token {token} of {schema_item} is not a valid float"
                    )
                return literal
        elif isinstance(schema_type, SchemaDefinedType):
            return self.load_defined_type(token, literal, schema_type)
        elif isinstance(schema_type, SchemaExpandable):
            if type(literal) != str:
                DBFormatError(
                    f"token {token} of {schema_type} is not a valid expandable str"
                )
            return self.load_expandable(token, literal, schema_type)
        elif isinstance(schema_type, SchemaRangeId):
            if type(literal) != int:
                DBFormatError(
                    f"token {token} of {schema_type} is not a valid rangeid integer"
                )
            return self.load_rangeid(token, literal, schema_type)
        elif isinstance(schema_type, SchemaContainerList):
            return self.load_list(token, literal, schema_type)
        elif isinstance(schema_type, SchemaObject):
            return self.load_object(token, literal, schema_type)
        elif isinstance(schema_type, SchemaReference):
            return self.load_reference(token, literal, schema_type)
        raise DBFormatError(
            f"Unknow literal {literal} for token {token} for type {schema_type}"
        )

    def load_defined_type(self, token, literal, schema_type):
        return schema_type.parse(literal)

    def load_object(self, token, literal, schema_object):
        print(f"Loading object {token} with {literal} ({schema_object})")
        # is it expandable?
        if isinstance(schema_object, SchemaExpandableObject):
            obj = type(
                f"{self._prefix}Expandable{schema_object.name}",
                (DBExpandableObject,),
                dict(),
            )(self, schema_object)
        else:
            obj = type(
                f"{self._prefix}{schema_object.name}", (DBObject,), dict()
            )(self, schema_object)

        # load object attributes
        self.load_object_attributes(obj, literal, schema_object)

        # check all required properties are properly defined in obj attributes
        for prop in schema_object.properties:
            if prop.required and not hasattr(obj, prop.name):
                raise DBFormatError(
                    f"Property {prop.name} is required in schema for object {schema_object}"
                )
        # add object to db indexes
        if schema_object.name not in self._indexes:
            self._indexes[schema_object.name] = []
        self._indexes[schema_object.name].append(obj)
        return obj

    def load_object_attributes(self, obj, content, schema_object):
        for token, literal in content.items():
            token_property = schema_object.prop(token)
            if token_property is None:
                # try expandable
                if token.endswith('[]'):
                    token_property = schema_object.prop(token[:-2])
                    if token_property is None:
                        raise DBFormatError(
                            f"Property {token} is not defined in schema for object {schema_object}"
                        )
                    if not isinstance(token_property.type, SchemaExpandable):
                        raise DBFormatError(
                            f"Property {token} is not expandable in schema for object {schema_object}"
                        )
                else:
                    raise DBFormatError(
                        f"Property {token} is not defined in schema for object {schema_object}"
                    )
            attribute = self.load_type(token, literal, token_property)
            if token.endswith('[]'):
                setattr(obj, token[:-2], attribute)
            else:
                setattr(obj, token, attribute)

    def load_reference(self, token, literal, schema_type: SchemaReference):
        all_objs = self.find_objects(schema_type.obj)
        for _obj in all_objs:
            attribute_value = getattr(_obj, schema_type.attribute)

            if isinstance(schema_type.obj, SchemaExpandableObject):
                print(
                    f"Object {schema_type.obj} is expandable, looking for attribute {attribute_value}"
                )
                if isinstance(attribute_value, DBObjectRange):
                    print(
                        f"Attribute {attribute_value} is a range, looking for members"
                    )
                    if literal in attribute_value.expanded():
                        return _obj
            elif attribute_value == literal:
                return _obj
        raise DBFormatError(
            f"Unable to find {token} reference with value {literal}"
        )

    def load_list(self, token, literal, schema_object):
        if type(literal) != list:
            raise DBFormatError(f"{schema_object.name}.{token} must be a list")
        result = []
        for item in literal:
            result.append(self.load_type(token, item, schema_object.content))
        return result

    def load_expandable(self, token, literal, schema_type):
        return type(f"{self._prefix}ExpandableRange", (DBObjectRange,), dict())(
            literal
        )

    def load_rangeid(self, token, literal, schema_type):
        return type(f"{self._prefix}RangeId", (DBObjectRangeId,), dict())(
            literal
        )

    def dump(self):

        print("DB:")
        super().dump(indent=2)

    def find_objects(self, object_type):
        return self._indexes[object_type.name]
