# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

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


class RacksDBNodeBase:
    @property
    def tags(self):
        result = DBList()
        for tag in getattr(self._parent, "tags", []):
            result.append(tag)
        # RacksDBNodeBase loaded tags are renamed with loaded prefix to avoid
        # conflict with this property.
        for tag in getattr(self, f"{self.LOADED_PREFIX}tags", []):
            result.append(tag)
        return result

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


class RacksDBDatacenterRoomRackBase:

    COMPUTED_PROPERTIES = ["nodes", "fillrate"]

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
