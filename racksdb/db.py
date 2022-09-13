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

from .errors import RacksDBFormatError
from .schema import (
    SchemaNativeType,
    SchemaDefinedType,
    SchemaContainerList,
    SchemaExpandable,
    SchemaRangeId,
    SchemaObject,
    SchemaExpandableObject,
    SchemaReference,
    SchemaItemSpec,
)


class DBObject:
    def dump(self, indent):
        for attribute, value in vars(self).items():
            if isinstance(value, list):
                print(f"{' '*indent}{attribute}:")
                for item in value:
                    if isinstance(item, DBObject):
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
    pass


class DBObjectRange:
    def __init__(self, rangeset):
        self.rangeset = NodeSet(rangeset)

    def expanded(self):
        return list(self.rangeset)


class DBObjectRangeId:
    def __init__(self, start):
        self.start = start

    def index(self, value):
        return start + value


class GenericDB(DBObject):
    def __init__(self, prefix, content, schema):
        self._prefix = prefix
        self._schema = schema
        self._indexes = {}  # objects indexes
        for token, value in content.items():
            schema_item = schema.content.item(token)
            if schema_item is None:
                raise RacksDBFormatError(
                    f"key {key} is not defined in schema {schema_object.name}"
                )
            attribute = self.load_item(token, value, schema_item.type)
            setattr(self, token, attribute)

    def load_item(
        self, token, value, schema_arg: Union[SchemaItemSpec, SchemaNativeType]
    ):
        if isinstance(schema_arg, SchemaItemSpec):
            schema_type = schema_arg.type
        else:
            schema_type = schema_arg
        print(f"Loading item {token} ({schema_type})")
        if isinstance(schema_type, SchemaNativeType):
            if schema_type.native is str:
                if type(value) != str:
                    RacksDBFormatError(
                        f"token {token} of {schema_type} is not a valid str"
                    )
                return value
            elif schema_type.native is int:
                if type(value) != int:
                    RacksDBFormatError(
                        f"token {token} of {schema_type} is not a valid int"
                    )
                return value
            elif schema_type.native is float:
                if type(value) != float:
                    RacksDBFormatError(
                        f"token {token} of {schema_item} is not a valid float"
                    )
                return value
        elif isinstance(schema_type, SchemaDefinedType):
            return self.load_defined_type(token, value, schema_type)
        elif isinstance(schema_type, SchemaExpandable):
            if type(value) != str:
                RacksDBFormatError(
                    f"token {token} of {schema_type} is not a valid expandable str"
                )
            return self.load_expandable(token, value, schema_type)
        elif isinstance(schema_type, SchemaRangeId):
            if type(value) != int:
                RacksDBFormatError(
                    f"token {token} of {schema_type} is not a valid rangeid integer"
                )
            return self.load_rangeid(token, value, schema_type)
        elif isinstance(schema_type, SchemaContainerList):
            return self.load_list(token, value, schema_type)
        elif isinstance(schema_type, SchemaObject):
            return self.load_object(token, value, schema_type)
        elif isinstance(schema_type, SchemaReference):
            return self.load_reference(token, value, schema_type)
        raise RacksDBFormatError(
            f"Unknow value {value} for token {token} for type {schema_type}"
        )

    def load_defined_type(self, token, value, schema_item):
        re.compile(schema_item.regex)
        return None

    def load_object(self, _token, _value, schema_object):
        print(f"Loading object {_token} with {_value} ({schema_object})")
        # is it expandable?
        if isinstance(schema_object, SchemaExpandableObject):
            obj = type(
                f"{self._prefix}Expandable{schema_object.name}",
                (DBExpandableObject,),
                dict(),
            )()
        else:
            obj = type(
                f"{self._prefix}{schema_object.name}", (DBObject,), dict()
            )()
        for token, value in _value.items():
            attribute_item = schema_object.item(token)
            if attribute_item is None:
                # try expandable
                if token.endswith('[]'):
                    attribute_item = schema_object.item(token[:-2])
                    if attribute_item is None:
                        raise RacksDBFormatError(
                            f"token {token} is not defined in schema for object {schema_object}"
                        )
                    if not isinstance(attribute_item.type, SchemaExpandable):
                        raise RacksDBFormatError(
                            f"token {token} is not expandable in schema for object {schema_object}"
                        )
                else:
                    raise RacksDBFormatError(
                        f"token {token} is not defined in schema for object {schema_object}"
                    )
            attribute = self.load_item(token, value, attribute_item)
            if token.endswith('[]'):
                setattr(obj, token[:-2], attribute)
            else:
                setattr(obj, token, attribute)
        # add object to db indexes
        if schema_object.name not in self._indexes:
            self._indexes[schema_object.name] = []
        self._indexes[schema_object.name].append(obj)
        return obj

    def load_reference(self, token, value, schema_type: SchemaReference):
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
                    if value in attribute_value.expanded():
                        return _obj
            elif attribute_value == value:
                return _obj
        raise RacksDBFormatError(
            f"Unable to find {token} reference with value {value}"
        )

    def load_list(self, token, value, schema_object):
        if type(value) != list:
            raise RacksDBFormatError(
                f"{schema_object.name}.{token} must be a list"
            )
        result = []
        for item in value:
            result.append(self.load_item(token, item, schema_object.content))
        return result

    def load_expandable(self, token, value, schema_type):
        return type(f"{self._prefix}ExpandableRange", (DBObjectRange,), dict())(
            value
        )

    def load_rangeid(self, token, value, schema_type):
        return type(f"{self._prefix}RangeId", (DBObjectRangeId,), dict())(value)

    def dump(self):

        print("DB:")
        super().dump(indent=2)

    def find_objects(self, object_type):
        return self._indexes[object_type.name]

    @classmethod
    def load(cls, prefix, path, schema):
        with open(path) as fh:
            try:
                content = yaml.safe_load(fh)
                return cls(prefix, content, schema)
            except yaml.composer.ComposerError as err:
                raise RacksDBFormatError(err)
