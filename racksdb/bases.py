# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

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
        result = DBList()
        for part in self.layout:
            # Iterate over nodes to expand nodesets, instead of adding
            # part.nodes to result.
            for node in part.nodes:
                result.append(node)
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
