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

import yaml

from .db import DBObject, DBObjectRange, DBObjectRangeId


class DBDumper:
    def __init__(self, objects_map={}):
        self._setup()
        self.objects_map = objects_map

    def _represent_dbobject(self, dumper, data):

        # override to dump map with item in any types
        value = []
        # tag = u'tag:yaml.org,2002:map'
        tag = f"{data.__class__.__name__}"
        node = yaml.MappingNode(tag, value)

        if dumper.alias_key is not None:
            dumper.represented_objects[dumper.alias_key] = node

        for item_key, item_value in vars(data).items():
            # skip special fields
            if item_key in ['_db', '_indexes', '_schema']:
                continue
            node_key = dumper.represent_data(item_key)

            if item_value.__class__.__name__ in self.objects_map.keys():
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
        # Disable objects aliasing with ids
        yaml.representer.ignore_aliases = lambda *data: True
        yaml.add_multi_representer(DBObject, self._represent_dbobject)
        yaml.add_multi_representer(DBObjectRange, self._represent_dbobjectrange)
        yaml.add_multi_representer(
            DBObjectRangeId, self._represent_dbobjectrangeid
        )

    def dump(self, data):
        noalias_dumper = yaml.dumper.Dumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        return yaml.dump(data, Dumper=noalias_dumper)
