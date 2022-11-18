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

from .generic.db import DBList


class RacksDBDatacenterBase:
    @property
    def tags(self):
        return [tag for tag in getattr(self, f"{self.LOADED_PREFIX}tags", [])]

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
        result = DBList([])
        for part in self.layout:
            # Iterate over nodes to expand nodesets, instead of adding
            # part.nodes to result.
            for node in part.nodes:
                result.items.append(node)
        return result

    @property
    def tags(self):
        return [tag for tag in getattr(self, f"{self.LOADED_PREFIX}tags", [])]

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
        result = []
        for tag in getattr(self._parent, 'tags', []):
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
        if (
            infrastructure is not None
            and infrastructure != self.infrastructure.name
        ):
            return False
        # filter by tags
        if tags is not None:
            for tag in tags:
                if tag not in self.tags:
                    return False
        return True
