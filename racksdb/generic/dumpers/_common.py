# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from typing import Dict, Union


class MapperDumper:
    def __init__(self, objects_map: Dict[str, Union[str, None]]):
        self.objects_map = objects_map

    def map(self, obj, prop, value):
        found = False
        if f"{obj.__class__.__name__}.{prop}" in self.objects_map.keys():
            target = self.objects_map[f"{obj.__class__.__name__}.{prop}"]
            found = True
        if value.__class__.__name__ in self.objects_map.keys():
            target = self.objects_map[value.__class__.__name__]
            found = True
        if found:
            # If the object is mapped to None, discard the attribute and
            # continue to the next one.
            if target is None:
                return None
            # Else, map the object to one of its attribute.
            return getattr(value, target)
        # Mapping not found, return value unmodified.
        return value
