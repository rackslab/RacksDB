# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import math

try:
    from functools import cached_property
except ImportError:
    # For Python 3.[6-7] compatibility. The dependency to cached_property
    # external library is not declared in pyproject.toml, it is added
    # explicitely in packages codes only for distributions stuck with these old
    # versions of Python.
    #
    # This try/except block can be removed when support of Python < 3.8 is
    # dropped in RacksDB.
    from cached_property import cached_property

from .generic.db import DBList, DBDict


class RacksDBDatacenterBase:
    def _filter(self, name=None, tags=None):
        # filter by name
        if name is not None and name != self.name:
            return False
        # filter by tags
        if tags is not None:
            for tag in tags:
                if tag not in self.tags:
                    return False
        return True


class RacksDBInfrastructureBase:
    @property
    def nodes(self):
        result = DBDict()
        for part in self.layout:
            # Iterate over the keys of DBDict instead of the DBDict itself to
            # avoid triggering expansion of expandable objects at this stage.
            for key in part.nodes.keys():
                result[key] = part.nodes[key]
        return result

    def _filter(self, name=None, tags=None):
        # filter by name
        if name is not None and name != self.name:
            return False
        # filter by tags
        if tags is not None:
            for tag in tags:
                if tag not in self.tags:
                    return False
        return True


class RacksDBGenericEquipment:
    @property
    def tags(self):
        result = DBList()
        for tag in getattr(self._parent, "tags", []):
            result.append(tag)
        # RacksDB{Node,StorageEquipment,NetworkEquipment,MiscEquipment} loaded tags are
        # renamed with loaded prefix to avoid conflict with this property.
        for tag in getattr(self, f"{self.LOADED_PREFIX}tags", []):
            # Avoid duplicate tags that could be defined on both parent part and
            # equipment.
            if tag not in result:
                result.append(tag)
        return result

    @cached_property
    def position(self):
        obj = self._db.create_object_by_name("EquipmentPosition")
        obj.height = (
            self._first.slot
            - self.rack.type.initial
            + math.floor((self.slot - self._first.slot) * self.type.width)
            * self.type.height
        )
        obj.width = (self.slot - self._first.slot) % int(1 / self.type.width)
        return obj

    def _filter(self, infrastructure=None, name=None, tags=None):
        # filter by name
        if name is not None and name != self.name:
            return False
        # filter by infrastructure name
        if infrastructure is not None and infrastructure != self.infrastructure.name:
            return False
        # filter by tags
        if tags is not None:
            for tag in tags:
                if tag not in self.tags:
                    return False
        return True


class RacksDBNodeBase(RacksDBGenericEquipment):
    pass


class RacksDBStorageEquipmentBase(RacksDBGenericEquipment):
    pass


class RacksDBNetworkEquipmentBase(RacksDBGenericEquipment):
    pass


class RacksDBMiscEquipmentBase(RacksDBGenericEquipment):
    pass


class RacksDBRackBase:
    def _filter(self, name=None):
        # filter by name
        if name is not None and name != self.name:
            return False
        return True

    @property
    def fillrate(self):
        """Return the fill rate of the rack as a float normalized between 0 and 1."""
        occupied = 0.0
        for infrastructure in self._db.infrastructures:
            for part in infrastructure.layout:
                if self.name == part.rack.name:
                    for equipment in part.nodes:
                        occupied += equipment.type.height * equipment.type.width
                    for equipment in part.storage:
                        occupied += equipment.type.height * equipment.type.width
                    for equipment in part.network:
                        occupied += equipment.type.height * equipment.type.width
                    for equipment in part.misc:
                        occupied += equipment.type.height * equipment.type.width
        return occupied / self.type.slots

    @property
    def nodes(self):
        result = DBList()
        # add reference to infrastructures nodes
        for infrastructure in self._db.infrastructures:
            for part in infrastructure.layout:
                if self.name == part.rack.name:
                    for nodes in part.nodes.values():
                        result.append(nodes)
        return result


class RacksDBRacksRowBase:
    @property
    def nbracks(self):
        """Return the number of racks in the row."""
        return len(self.racks)
