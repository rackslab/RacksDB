# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List, Dict, Union

from .errors import DBViewError


class DBViewParameter:
    def __init__(
        self, name, description, short=None, _type=None, default=None, choices=None
    ):
        self.name = name
        self.description = description
        self.short = short
        self.type = _type
        self.default = default
        self.choices = choices


class DBViewFilter:
    def __init__(
        self, name: str, description: str, nargs: Union[str, int, None] = None
    ):
        self.name = name
        self.description = description
        self.nargs = nargs


class DBView:
    def __init__(
        self,
        content: str,
        description: str,
        filters: List[DBViewFilter],
        objects_map: Dict[str, Union[None, str]],
    ):
        self.content = content
        self.description = description
        self.filters = filters
        self.objects_map = objects_map


class DBViewSet:
    def __iter__(self):
        for view in self.VIEWS:
            yield view

    def parameters(self):
        for parameter in self.PARAMETERS:
            yield parameter

    def __getitem__(self, key):
        for view in self.VIEWS:
            if view.content == key:
                return view
        raise DBViewError(f"Unable to find view for '{key}' content")
