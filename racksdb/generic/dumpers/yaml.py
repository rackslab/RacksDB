# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import logging

import yaml

from ._common import MapperDumper
from ..db import DBObject, DBObjectRange, DBObjectRangeId, DBList, DBDict
from ..schema import SchemaObject
from ..definedtype import SchemaDefinedType

logger = logging.getLogger(__name__)


class DBDumperYAML(MapperDumper):
    def __init__(self, show_types=False, objects_map={}, fold=True):
        super().__init__(objects_map)
        self.show_types = show_types
        self.fold = fold
        self._setup()
        # refs to last represented objects, used to inform users in case of dump
        # recursion loops
        self._last_objs = collections.deque([], 8)

    def _represent_list(self, dumper, data):

        tag = "tag:yaml.org,2002:seq"
        if self.fold:
            value = [dumper.represent_data(_object) for _object in data.itervalues()]
        else:
            value = [dumper.represent_data(_object) for _object in data]
        return yaml.SequenceNode(tag, value)

    def _represent_dict(self, dumper, data):
        # DBDict are rendered like a list, as well as they are represented in
        # database.
        tag = "tag:yaml.org,2002:seq"
        if self.fold:
            value = [dumper.represent_data(_object) for _object in data.values()]
        else:
            value = [dumper.represent_data(_object) for _object in data]
        return yaml.SequenceNode(tag, value)

    def _fill_obj_node_value(self, dumper, node_value, obj, prop, value):
        # Check the object is mapped to one of its attribute or None.
        value = self.map(obj, prop, value)
        if value is None:
            return
        node_value.append((dumper.represent_data(prop), dumper.represent_data(value)))

    def _represent_dbobject(self, dumper, data):

        self._last_objs.append(type(data).__name__)
        node_value = []
        if self.show_types:
            tag = f"{data.__class__.__name__}"
        else:
            tag = "tag:yaml.org,2002:map"  # YAML generic mapping type

        node = yaml.MappingNode(tag, node_value)

        for item_key, item_value in vars(data).items():
            # skip special fields
            if item_key in [
                "_db",
                "_indexes",
                "_schema",
                "_parent",
                "_first",
                "_key",
            ]:
                continue
            # If the attribute has been renamed with loaded prefix, call bases
            # module class attribute instead.
            if item_key.startswith(data.LOADED_PREFIX):
                item_key = item_key[len(data.LOADED_PREFIX) :]
                item_value = getattr(data, item_key)
            self._fill_obj_node_value(dumper, node_value, data, item_key, item_value)

        for prop in data._computed_props():
            self._fill_obj_node_value(
                dumper, node_value, data, prop, getattr(data, prop)
            )
        return node

    def _represent_dbobjectrange(self, dumper, data):
        return dumper.represent_data(str(data.rangeset))

    def _represent_dbobjectrangeid(self, dumper, data):
        return dumper.represent_data(data.start)

    def _setup(self):
        yaml.add_representer(DBDict, self._represent_dict)
        yaml.add_representer(DBList, self._represent_list)
        yaml.add_multi_representer(DBObject, self._represent_dbobject)
        yaml.add_multi_representer(DBObjectRange, self._represent_dbobjectrange)
        yaml.add_multi_representer(DBObjectRangeId, self._represent_dbobjectrangeid)

    def dump(self, data):
        noalias_dumper = yaml.dumper.Dumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        try:
            # Remove last newline to avoid double newline when printed by CLI.
            return yaml.dump(data, Dumper=noalias_dumper).rstrip()
        except RecursionError:
            logger.error(
                "Recursion loop detected during dump, last represented objects:"
                "\n→ %s",
                "\n→ ".join(self._last_objs),
            )
            return ""


class SchemaDumperYAML:
    def __init__(self):
        self._setup()

    def _represent_schemadefinedtype(self, dumper, data):
        tag = "tag:yaml.org,2002:str"  # YAML generic string type
        node = yaml.ScalarNode(tag, data.pattern)
        return node

    def _setup(self):
        yaml.add_multi_representer(SchemaDefinedType, self._represent_schemadefinedtype)

    def dump(self, schema):
        noalias_dumper = yaml.dumper.Dumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        # Dump all Schema object content except _schema attribute. Remove last newline
        # to avoid double newline when printed by CLI.
        return yaml.dump(
            {**schema._schema, **{"_types": schema.types}},
            Dumper=noalias_dumper,
        ).rstrip()
