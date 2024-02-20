# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import copy
import logging

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


def deepmerge(a: dict, b: dict, path=[]) -> dict:
    """Deep-merge dict b into dict a."""
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                deepmerge(a[key], b[key], path + [str(key)])
            elif a[key] != b[key]:
                raise Exception("Conflict at " + ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


class DBObject:
    LOADED_PREFIX = "__loaded_"

    def __init__(self, db, schema):
        self._db = db
        self._schema = schema

    def _filter(self, **kwargs):
        """Abstract filter method, must be overriden in specialized bases module
        classes when filtering is needed."""
        return True

    def _computed_props(self):
        """Generator to iterate over the list of DBObject computed properties."""
        if hasattr(self, "COMPUTED_PROPERTIES"):
            for prop in self.COMPUTED_PROPERTIES:
                yield prop


class DBExpandableObject(DBObject):
    def _attributes(self):
        """Return the dict of stable attributes, range attribues and the pair of range
        attribute and value."""
        stable_attributes = {}
        range_attribute = None
        rangeid_attributes = {}
        for attribute, value in vars(self).items():
            # Skip selection of special _key attribute at this stage, it is
            # handled later when attributes are set on freshly instanciated
            # object.
            if attribute == "_key":
                continue
            if isinstance(value, DBObjectRange):
                range_attribute = (attribute, value)
            elif isinstance(value, DBObjectRangeId):
                rangeid_attributes[attribute] = value
            else:
                stable_attributes[attribute] = value
        return stable_attributes, range_attribute, rangeid_attributes

    def _instanciate_obj(
        self, index, value, range_attribute, rangeid_attributes, stable_attributes
    ):
        """Instanciate the object at the given index."""

        _attributes = stable_attributes.copy()
        _attributes[range_attribute[0]] = value
        for rangeid_name, rangeid_value in rangeid_attributes.items():
            _attributes[rangeid_name] = rangeid_value.index(index)

        bases = [DBObject]
        # Add provided module base if defined
        try:
            # Insert bases module class in the beginning of the list to make
            # sure methods from this classes are called over the methods from
            # DBObject.
            bases.insert(
                0,
                getattr(
                    self._db._bases,
                    f"{self._db._prefix}{self._schema.name}Base",
                ),
            )
        except AttributeError:
            pass
        obj = type(f"{self._db._prefix}{self._schema.name}", tuple(bases), dict())(
            self._db, self._schema
        )
        for attr_name, attr_value in _attributes.items():
            setattr(obj, attr_name, attr_value)
            # Set object _key attribute if property is a key
            prop = self._schema.prop(attr_name)
            if prop is not None and prop.key:
                setattr(obj, "_key", attr_value)
        return obj

    def objects(self):
        """Return the list of all expanded objects."""
        result = []
        stable_attributes, range_attribute, rangeid_attributes = self._attributes()
        first = None
        for index, value in enumerate(range_attribute[1].expanded()):
            obj = self._instanciate_obj(
                index, value, range_attribute, rangeid_attributes, stable_attributes
            )
            if first is None:
                first = obj
            setattr(obj, "_first", first)
            result.append(obj)
        return result

    def getobject(self, key):
        """Return an instance of the object with provided key. The first object is also
        instanciated and linked in _first attribute."""
        stable_attributes, range_attribute, rangeid_attributes = self._attributes()
        first = None
        for index, value in enumerate(range_attribute[1].expanded()):
            if first and value != key:
                continue
            obj = self._instanciate_obj(
                index, value, range_attribute, rangeid_attributes, stable_attributes
            )
            if first is None:
                first = obj
            setattr(obj, "_first", first)
            if value == key:
                return obj

        raise KeyError(f"key '{key}' not found in {str(range_attribute[1])}")


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


class DBList(list):
    def __iter__(self):
        for item in super().__iter__():
            if isinstance(item, DBExpandableObject):
                for expanded_item in item.objects():
                    yield expanded_item
            else:
                yield item

    def __len__(self):
        """Return the number of values in the list."""
        return len([value for value in self])

    def itervalues(self):
        """Additional iterators over the list values that does not trigger expansion of
        DBExpandableObjects."""
        for item in super().__iter__():
            yield item

    def filter(self, **kwargs):
        """Return a copy of the current DBList without values that do not match provided
        filter criteria."""
        result = DBList()
        for item in self:
            if item._filter(**kwargs):
                result.append(item)
        return result


class DBDict(dict):
    def filter(self, **kwargs):
        """Return a copy of the current DBDict without key and values that do not match
        provided filter criteria."""
        result = DBDict()
        for key, value in self.items():
            if value._filter(**kwargs):
                result[key] = value
        return result

    def __iter__(self):
        for item in self.values():
            if isinstance(item, DBExpandableObject):
                for expanded_item in item.objects():
                    yield expanded_item
            else:
                yield item

    def __getitem__(self, key):
        # Try to get the item from parent dict. If the key cannot be found in dict,
        # search for the key in all DBObjectRange keys. If found, return an instance
        # of this particular expanded object.
        try:
            return super().__getitem__(key)
        except KeyError:
            for _key in self.keys():
                if isinstance(_key, DBObjectRange) and key in _key.rangeset:
                    return super().__getitem__(_key).getobject(key)
            raise KeyError(key)

    def __len__(self):
        """Return the number of values in the dictionnary. It counts the number of
        values in expandable objects by counting the number of values in the rangeset
        without requiring instanciating of objects in memory."""
        values = 0
        for key in self.keys():
            if isinstance(key, DBObjectRange):
                values += len(key.rangeset)
            else:
                values += 1
        return values

    def first(self):
        """Return the first expanded object of the dictionnary."""
        return list(self)[0]  # list() calls __iter__()


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
            if not path.name.endswith(".yml"):
                raise DBFormatError(f"DB contains file {path} without .yml extension")
            logger.debug("Loading DB file %s", path)
            self.content = DBFileLoader(path).content
        elif path.suffix == ".l":
            self.content = []
            for item in path.iterdir():
                self.content.append(DBSplittedFilesLoader(item).content)
        else:
            # if directory, load recursively
            self.content = {}
            for item in path.iterdir():
                logger.debug("Loading DB directory %s", path)
                self.content[item.stem] = DBSplittedFilesLoader(item).content


class DBDictsLoader:
    """Loader that loads data from an optional set of dictionaries nothing. It accepts
    any number of dictionaries in argument, they are all deep merged consecutively. It
    can be used to load optional database files (ie. potentially empty database) when
    schema defines enough default values to operate or when initial data is loaded by
    other mean."""

    def __init__(self, *args):
        self.content = {}
        for _content in args:
            self.content = deepmerge(copy.deepcopy(self.content), _content)


class DBStdinLoader:
    """Load YAML database provided in program's standard input."""

    def __init__(self):
        try:
            self.content = yaml.safe_load(sys.stdin.read())
        except yaml.composer.ComposerError as err:
            raise DBFormatError(err)


class DBStringLoader:
    """Load YAML database provided in a string."""

    def __init__(self, content, initial={}):
        try:
            self.content = deepmerge(initial, yaml.safe_load(content))
        except yaml.composer.ComposerError as err:
            raise DBFormatError(err)


class GenericDB(DBObject):
    def __init__(self, prefix, schema, bases=None):
        super().__init__(self, schema)
        self._prefix = prefix
        # Module of base classes for instanciated DB objects
        self._bases = bases
        self._indexes = {}  # objects indexes
        # Set of SchemaObjects for which objects have been already loaded,
        # including SchemaObjects of optional objects not present in database.
        self._loaded_classes = set()

    def load(self, loader):
        obj = self.load_object("_root", loader.content, self._schema.content, None)
        for key, value in vars(obj).items():
            # Copy loaded object attributes to self GenericDB object, except
            # _schema where we want to keep Schema object instead of loaded
            # SchemaObject.
            if key != "_schema":
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
            if not isinstance(literal, str):
                DBFormatError(
                    f"token {token} of {schema_type} is not a valid expandable str"
                )
            return self.load_expandable(literal)
        elif isinstance(schema_type, SchemaRangeId):
            if not isinstance(literal, int):
                DBFormatError(
                    f"token {token} of {schema_type} is not a valid rangeid integer"
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
        logger.debug("Loading object %s with %s (%s)", token, literal, schema_object)
        # is it expandable?
        if schema_object.expandable:
            bases = [DBExpandableObject]
            classname = f"{self._prefix}Expandable{schema_object.name}"
        else:
            bases = [DBObject]
            classname = f"{self._prefix}{schema_object.name}"
        # Add provided module base if defined
        try:
            # Insert bases module class in the beginning of the list to make
            # sure methods from this classes are called over the methods from
            # DBObject.
            bases.insert(
                0,
                getattr(self._bases, f"{self._prefix}{schema_object.name}Base"),
            )
        except AttributeError:
            pass
        # instanciate the object with its dynamically defined class
        obj = type(classname, tuple(bases), dict())(self, schema_object)

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
            # Load back references
            if isinstance(prop.type, SchemaBackReference):
                setattr(obj, prop.name, self.load_back_reference(obj, prop.type))
            # Assign default value to optional properties when provided in
            # schema.
            if not hasattr(obj, prop.name) and prop.default is not None:
                value = self.load_type(prop.name, prop.default, prop.type, obj)
                logger.debug(
                    "Assigning object %s property %s default value %s",
                    schema_object,
                    prop.name,
                    value,
                )
                setattr(obj, prop.name, value)
            # If property is a key, check value uniqueness and set object _key
            # attribute.
            if prop.key:
                value = getattr(obj, prop.name)
                # If another object of the same type is already present in index
                if schema_object.name in self._indexes:
                    # Check over all previously loaded objects of the same type
                    # if this key value has not been used yet.
                    for _obj in self._indexes[schema_object.name]:
                        if getattr(_obj, prop.name) == value:
                            raise DBFormatError(
                                f"Key value {value} of {schema_object} is not "
                                "unique."
                            )
                setattr(obj, "_key", value)

        # add object to db indexes
        if schema_object.name not in self._indexes:
            self._indexes[schema_object.name] = []
        self._indexes[schema_object.name].append(obj)
        self._loaded_classes |= schema_object.subobjs
        logger.debug("Loaded classes: %s", [cls.name for cls in self._loaded_classes])
        return obj

    def load_object_attributes(self, obj, content, schema_object: SchemaObject):

        try:
            _content = content.copy()
        except AttributeError:
            raise DBFormatError(
                f"Unable to copy object {obj.__class__.__name__} attributes "
                f"({type(content)})"
            )
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
                token_property = self.token_object_property(token, schema_object)
                # Check if this attribute can be loaded, considering its
                # references and loaded objects.
                if not self.loadable_attribute(token, token_property, passes, obj):
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

                attribute = self.load_type(token, literal, token_property.type, obj)
                if token.endswith("[]"):
                    token = token[:-2]
                # Check the bases module class does not already provide a
                # conflicting attribute with the same name. In this case, it is
                # renamed with LOADED_PREFIX.
                if hasattr(obj, token):
                    logger.debug(
                        "Renaming object attribute %s.%s with prefix %s",
                        obj,
                        token,
                        obj.LOADED_PREFIX,
                    )
                    token = obj.LOADED_PREFIX + token
                setattr(obj, token, attribute)
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
            # sub-objects and not available in set of already loaded objects,
            # the attribute cannot be loaded (yet).
            for ref in subtype.refs - subtype.subobjs:
                if ref not in self._loaded_classes:
                    logger.debug(
                        "Found undefined reference to %s in property %s in pass %d",
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

        logger.debug("Found objects for type %s: %s", schema_type.obj.name, all_objs)
        for _obj in all_objs:
            property_value = getattr(_obj, schema_type.prop)
            if property_value == literal:
                return _obj
        raise DBFormatError(f"Unable to find {token} reference with value {literal}")

    def load_back_reference(self, parent, schema_type: SchemaBackReference):
        logger.debug("Loading back reference of %s/%s", parent, schema_type)
        while parent._schema is not schema_type.obj and parent is not None:
            logger.debug("Back reference %s != %s", parent._schema, schema_type.obj)
            parent = parent._parent

        # If the SchemaBackReference has a property, return the reference to
        # this object property, or return the reference to the whole object.
        if schema_type.prop is not None:
            return getattr(parent, schema_type.prop)
        else:
            return parent

    def load_list(self, token, literal, schema_object: SchemaContainerList, parent):
        # Check the literal is a valid list
        if not isinstance(literal, list):
            # If it is not a list, it must be a dict and the contained object must have
            # a key property. In this case, the literal is transformed into a list of
            # dictionnaries augmented with object key property. Then it is loaded
            # exactly the same way as if it was declared in database as a list with the
            # key property.
            if isinstance(literal, dict) and schema_object.content.has_key():
                logger.debug(
                    "Transforming dictionnary into a list of %s with key property",
                    schema_object.content,
                )
                literal = [
                    {**{schema_object.content.key_property(): key}, **value}
                    for key, value in literal.items()
                ]
            else:
                raise DBFormatError(f"token {token} {schema_object} must be a list")
        # Check if the contained object has a key property
        has_key = False
        if isinstance(schema_object.content, SchemaObject):
            for prop in schema_object.content.properties:
                if prop.key:
                    has_key = True
        # If the contained object has a key, instanciate and fill a DBDict that
        # can be subscripted with the key.
        if has_key:
            result = DBDict()
            for item in literal:
                content = self.load_type(token, item, schema_object.content, parent)
                result[content._key] = content
            return result
        # Otherwise, instanciated a simple DBList.
        else:
            result = DBList()
            for item in literal:
                result.append(
                    self.load_type(token, item, schema_object.content, parent)
                )
            return result

    def load_expandable(self, literal):
        return type(f"{self._prefix}ExpandableRange", (DBObjectRange,), dict())(literal)

    def load_rangeid(self, literal):
        return type(f"{self._prefix}RangeId", (DBObjectRangeId,), dict())(literal)

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
