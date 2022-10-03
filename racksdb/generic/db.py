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
import logging
from typing import List

import yaml
from ClusterShell.NodeSet import NodeSet

from .errors import DBFormatError
from .definedtype import SchemaDefinedType
from .schema import (
    SchemaGenericValueType,
    SchemaNativeType,
    SchemaContainerList,
    SchemaExpandable,
    SchemaRangeId,
    SchemaObject,
    SchemaReference,
    SchemaBackReference,
    SchemaProperty,
)

logger = logging.getLogger(__name__)


class DBObject:
    def __init__(self, db, schema):
        self._db = db
        self._schema = schema


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

        first = None
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
            if first is None:
                first = obj
            setattr(obj, '_first', first)
        return result


class DBObjectRange:
    def __init__(self, rangeset):
        self.rangeset = NodeSet(rangeset)

    def expanded(self):
        return list(self.rangeset)

    def __repr__(self):
        return str(self.rangeset)


class DBObjectRangeId:
    def __init__(self, start):
        self.start = start

    def index(self, value):
        return self.start + value


class DBList:
    def __init__(self, items: List):
        self.items = items

    def __iter__(self):
        for item in self.items:
            if isinstance(item, DBExpandableObject):
                for expanded_item in item.objects():
                    yield expanded_item
            else:
                yield item

    def __getitem__(self, id):
        return self.items[id]


class DBFileLoader:
    def __init__(self, path):
        with open(path) as fh:
            try:
                self.content = yaml.safe_load(fh)
            except yaml.composer.ComposerError as err:
                raise DBFormatError(err)


class DBSplittedFilesLoader:
    def __init__(self, path):
        # try the parent folder
        if not path.exists():
            raise DBFormatError(f"DB path {path} does not exist")
        elif path.is_file():
            if not path.name.endswith('.yml'):
                raise DBFormatError(
                    f"DB contains file {path} without .yml extension"
                )
            logger.debug("Loading DB file %s", path)
            self.content = DBFileLoader(path).content
        elif path.suffix == '.l':
            self.content = []
            for item in path.iterdir():
                self.content.append(DBSplittedFilesLoader(item).content)
        else:
            # if directory, load recursively
            self.content = {}
            for item in path.iterdir():
                logger.debug("Loading DB directory %s", path)
                self.content[item.stem] = DBSplittedFilesLoader(item).content


class GenericDB(DBObject):
    def __init__(self, prefix, schema):
        super().__init__(self, schema)
        self._prefix = prefix
        self._indexes = {}  # objects indexes

    def load(self, loader):
        obj = self.load_object(
            '_root', loader.content, self._schema.content, None
        )
        for key, value in vars(obj).items():
            # Copy loaded object attributes to self GenericDB object, except
            # _schema where we want to keep Schema object instead of loaded
            # SchemaObject.
            if key != '_schema':
                setattr(self, key, value)

    def load_type(
        self,
        token,
        literal,
        schema_type: SchemaGenericValueType,
        parent,
    ):
        logger.debug("Loading type %s (%s)", token, schema_type)
        if isinstance(schema_type, SchemaNativeType):
            for native_type in [str, int, float, bool]:
                if schema_type.native is native_type:
                    if type(literal) != native_type:
                        raise DBFormatError(
                            f"{token} {literal} is not a valid "
                            f"{native_type.__name__}"
                        )
                    return literal
        elif isinstance(schema_type, SchemaDefinedType):
            return self.load_defined_type(literal, schema_type)
        elif isinstance(schema_type, SchemaExpandable):
            if type(literal) != str:
                DBFormatError(
                    f"token {token} of {schema_type} is not a valid expandable "
                    "str"
                )
            return self.load_expandable(literal)
        elif isinstance(schema_type, SchemaRangeId):
            if type(literal) != int:
                DBFormatError(
                    f"token {token} of {schema_type} is not a valid rangeid "
                    "integer"
                )
            return self.load_rangeid(literal)
        elif isinstance(schema_type, SchemaContainerList):
            return self.load_list(token, literal, schema_type, parent)
        elif isinstance(schema_type, SchemaObject):
            return self.load_object(token, literal, schema_type, parent)
        elif isinstance(schema_type, SchemaReference):
            return self.load_reference(token, literal, schema_type)
        elif isinstance(schema_type, SchemaBackReference):
            raise DBFormatError(
                f"Back reference {token} cannot be defined in database for "
                f"object {schema_type}"
            )
        raise DBFormatError(
            f"Unknow literal {literal} for token {token} for type {schema_type}"
        )

    def load_defined_type(self, literal, schema_type: SchemaDefinedType):
        return schema_type.parse(literal)

    def load_object(
        self, token, literal, schema_object: SchemaObject, parent: SchemaObject
    ):
        logger.debug(
            "Loading object %s with %s (%s)", token, literal, schema_object
        )
        # is it expandable?
        if schema_object.expandable:
            obj = type(
                f"{self._prefix}Expandable{schema_object.name}",
                (DBExpandableObject,),
                dict(),
            )(self, schema_object)
        else:
            obj = type(
                f"{self._prefix}{schema_object.name}", (DBObject,), dict()
            )(self, schema_object)

        obj._parent = parent

        # load object attributes
        self.load_object_attributes(obj, literal, schema_object)

        for prop in schema_object.properties:
            # Check all required properties are properly defined in obj
            # attributes.
            if (
                not isinstance(prop.type, SchemaBackReference)
                and prop.required
                and not hasattr(obj, prop.name)
            ):
                raise DBFormatError(
                    f"Property {prop.name} is required in schema for object "
                    f"{schema_object}"
                )
            # Assign default value to optional properties when provided in
            # schema.
            if not hasattr(obj, prop.name) and prop.default is not None:
                logger.debug(
                    "Assigning object %s property %s default value %s",
                    schema_object,
                    prop.name,
                    prop.default,
                )
                setattr(obj, prop.name, prop.default)

        # add object to db indexes
        if schema_object.name not in self._indexes:
            self._indexes[schema_object.name] = []
        self._indexes[schema_object.name].append(obj)
        return obj

    def load_object_attributes(self, obj, content, schema_object: SchemaObject):

        _content = content.copy()
        passes = 0

        while len(_content):
            # Pass number
            passes += 1
            # Flag to know if at least one attribute has been loaded in last
            # pass.
            processed = False

            # Iterate over a copy of last pass remaining object attributes
            for token, literal in _content.copy().items():
                # Get the schema property corresponding to this token
                token_property = self.token_object_property(
                    token, schema_object
                )
                # Check if this attribute can be loaded, considering its
                # references and loaded objects.
                if not self.loadable_attribute(
                    token, token_property, passes, obj
                ):
                    # The attribute cannot be loaded, jump to next attribute.
                    logger.debug(
                        "Skipping object %s property %s in pass %d",
                        schema_object.name,
                        token,
                        passes,
                    )
                    continue
                else:
                    # The attribute can be loaded, set the flag and remove the
                    # attribute from the dict for the next pass.
                    processed = True
                    del _content[token]

                attribute = self.load_type(
                    token, literal, token_property.type, obj
                )
                if token.endswith('[]'):
                    setattr(obj, token[:-2], attribute)
                else:
                    setattr(obj, token, attribute)
            # Load back references
            for prop in schema_object.properties:
                if isinstance(prop.type, SchemaBackReference):
                    setattr(
                        obj, prop.name, self.load_back_reference(obj, prop.type)
                    )
            # Check if at least one attribute has been loaded during this pass,
            # or raise DB format error exception.
            if not processed:
                raise DBFormatError(
                    f"Unable to load {token} {schema_object.name} after "
                    f"{passes} passes, probably because of circular references"
                )

    def token_object_property(
        self, token, schema_object: SchemaObject
    ) -> SchemaProperty:
        token_property = schema_object.prop(token)
        if token_property is None:
            # try expandable
            if token.endswith('[]'):
                token_property = schema_object.prop(token[:-2])
                if token_property is None:
                    raise DBFormatError(
                        f"Property {token} is not defined in schema for object "
                        f"{schema_object}"
                    )
                if not isinstance(token_property.type, SchemaExpandable):
                    raise DBFormatError(
                        f"Property {token} is not expandable in schema for "
                        f"object {schema_object}"
                    )
            else:
                raise DBFormatError(
                    f"Property {token} is not defined in schema for object "
                    f"{schema_object}"
                )
        return token_property

    def loadable_attribute(self, token, token_property, passes, obj):
        subtype = token_property.type
        # If the property is a list, check the content of the list.
        if isinstance(token_property.type, SchemaContainerList):
            subtype = token_property.type.content
        if isinstance(subtype, SchemaObject):
            # If one object reference is not defined in inspected object
            # sub-objects and not available in DB index, the attribute cannot be
            # loaded (yet).
            for ref in subtype.refs - subtype.subobjs:
                if ref.name not in self._indexes:
                    logger.debug(
                        "Found undefined reference to %s in property %s in "
                        "pass %d",
                        ref.name,
                        token,
                        passes,
                    )
                    return False
            # Check back references with properties are all loaded. If one back
            # reference with a property points to a property not already loaded
            # on back referenced object, the attribute cannot be loaded (yet).
            for prop in subtype.properties:
                if (
                    isinstance(prop.type, SchemaBackReference)
                    and prop.type.prop is not None
                ):
                    # Loop to find the back referenced object
                    while obj._schema is not prop.type.obj and obj is not None:
                        obj = obj._parent
                    # Check attribute is already defined on referenced object
                    if not hasattr(obj, prop.type.prop):
                        logger.debug(
                            "Found undefined back reference to %s.%s in "
                            "property %s in pass %d",
                            ref.name,
                            prop.type.prop,
                            token,
                            passes,
                        )
                        return False
        return True

    def load_reference(self, token, literal, schema_type: SchemaReference):
        all_objs = self.find_objects(schema_type.obj.name, expand=True)
        if all_objs is None:
            raise DBFormatError(
                f"Unable to find {token} {literal} reference because objects "
                f"{schema_type.obj.name} are missing in DB indexes"
            )

        logger.debug(
            "Found objects for type %s: %s", schema_type.obj.name, all_objs
        )
        for _obj in all_objs:
            property_value = getattr(_obj, schema_type.prop)
            if property_value == literal:
                return _obj
        raise DBFormatError(
            f"Unable to find {token} reference with value {literal}"
        )

    def load_back_reference(self, parent, schema_type: SchemaBackReference):
        logger.debug("Loading back reference of %s/%s", parent, schema_type)
        while parent._schema is not schema_type.obj and parent is not None:
            logger.debug(
                "Back reference %s != %s", parent._schema, schema_type.obj
            )
            parent = parent._parent

        # If the SchemaBackReference has a property, return the reference to
        # this object property, or return the reference to the whole object.
        if schema_type.prop is not None:
            return getattr(parent, schema_type.prop)
        else:
            return parent

    def load_list(
        self, token, literal, schema_object: SchemaContainerList, parent
    ):
        if type(literal) != list:
            raise DBFormatError(f"token {token} {schema_object} must be a list")
        result = []
        for item in literal:
            result.append(
                self.load_type(token, item, schema_object.content, parent)
            )
        return DBList(result)

    def load_expandable(self, literal):
        return type(f"{self._prefix}ExpandableRange", (DBObjectRange,), dict())(
            literal
        )

    def load_rangeid(self, literal):
        return type(f"{self._prefix}RangeId", (DBObjectRangeId,), dict())(
            literal
        )

    def find_objects(self, object_type_name, expand=False):
        if object_type_name not in self._indexes:
            return None
        result = []
        for obj in self._indexes[object_type_name]:
            if expand and isinstance(obj, DBExpandableObject):
                result += obj.objects()
            else:
                result.append(obj)
        return result
