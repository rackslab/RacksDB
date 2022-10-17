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

import collections
import logging

import yaml

from .db import DBObject, DBObjectRange, DBObjectRangeId, DBList
from .schema import Schema, SchemaObject
from .definedtype import SchemaDefinedType

logger = logging.getLogger(__name__)


class DBDumper:
    def __init__(self, show_types=False, objects_map={}, expand=False):
        self.show_types = show_types
        self.objects_map = objects_map
        self.expand = expand
        self._setup()
        # refs to last represented objects, used to inform users in case of dump
        # recursion loops
        self._last_objs = collections.deque([], 8)

    def _represent_expanded_list(self, dumper, data):

        value = []
        tag = u'tag:yaml.org,2002:seq'
        for _object in data:
            value.append(dumper.represent_data(_object))
        return yaml.SequenceNode(tag, value)

    def _represent_list(self, dumper, data):

        value = []
        tag = u'tag:yaml.org,2002:seq'
        for _object in data.items:
            value.append(dumper.represent_data(_object))
        return yaml.SequenceNode(tag, value)

    def _represent_dbobject(self, dumper, data):

        self._last_objs.append(type(data).__name__)
        value = []
        if self.show_types:
            tag = f"{data.__class__.__name__}"
        else:
            tag = u'tag:yaml.org,2002:map'  # YAML generic mapping type

        node = yaml.MappingNode(tag, value)

        for item_key, item_value in vars(data).items():
            # skip special fields
            if item_key in [
                '_db',
                '_indexes',
                '_schema',
                '_parent',
                '_first',
                '_key',
            ]:
                continue
            # If the attribute has been renamed with loaded prefix, call bases
            # module class attribute instead.
            if item_key.startswith(data.LOADED_PREFIX):
                item_key = item_key[len(data.LOADED_PREFIX):]
                item_value = getattr(data, item_key)
            node_key = dumper.represent_data(item_key)
            # Check the object is mapped to one of its attribute or None.
            if item_value.__class__.__name__ in self.objects_map.keys():
                # If the object is mapped to None, discard the attribute and
                # continue to the next one.
                if self.objects_map[item_value.__class__.__name__] is None:
                    continue
                # Else, map the object to one of its attribute.
                item_value = getattr(
                    item_value, self.objects_map[item_value.__class__.__name__]
                )
            node_value = dumper.represent_data(item_value)

            value.append((node_key, node_value))

        return node

    def _represent_dbobjectrange(self, dumper, data):
        return dumper.represent_data(str(data.rangeset))

    def _represent_dbobjectrangeid(self, dumper, data):
        return dumper.represent_data(data.start)

    def _setup(self):
        if self.expand:
            yaml.add_representer(DBList, self._represent_expanded_list)
        else:
            yaml.add_representer(DBList, self._represent_list)
        yaml.add_multi_representer(DBObject, self._represent_dbobject)
        yaml.add_multi_representer(DBObjectRange, self._represent_dbobjectrange)
        yaml.add_multi_representer(
            DBObjectRangeId, self._represent_dbobjectrangeid
        )

    def dump(self, data):
        noalias_dumper = yaml.dumper.Dumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        try:
            return yaml.dump(data, Dumper=noalias_dumper)
        except RecursionError:
            logger.error(
                "Recursion loop detected during dump, last represented objects:"
                "\n→ %s",
                "\n→ ".join(self._last_objs),
            )
            return ""


class SchemaDumper:
    def __init__(self):
        self._setup()

    def _represent_schemaobject(self, dumper, data):
        value = []
        tag = u'tag:yaml.org,2002:map'  # YAML generic mapping type
        node = yaml.MappingNode(tag, value)
        for prop in data.properties:
            value.append(
                (
                    dumper.represent_str(prop.name),
                    dumper.represent_str(str(prop)),
                )
            )
        return node

    def _represent_schemadefinedtype(self, dumper, data):
        tag = u'tag:yaml.org,2002:str'  # YAML generic string type
        node = yaml.ScalarNode(tag, data.pattern)
        return node

    def _setup(self):
        yaml.add_representer(SchemaObject, self._represent_schemaobject)
        yaml.add_multi_representer(
            SchemaDefinedType, self._represent_schemadefinedtype
        )

    def dump(self, schema):
        noalias_dumper = yaml.dumper.Dumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        # dump all Schema object content except _schema attribute
        return yaml.dump(
            {
                key: value
                for key, value in vars(schema).items()
                if key != '_schema'
            },
            Dumper=noalias_dumper,
        )
