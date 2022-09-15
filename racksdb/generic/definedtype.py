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

import re

from .errors import DBFormatError


class SchemaDefinedType:
    def __init__(self):
        self.name = self.__class__.__module__

    def __str__(self):
        return f"~{self.name}"

    def _match(self, value):
        regex = re.compile(self.pattern)
        match = regex.match(value)
        if match is None:
            raise DBFormatError(
                f"Unable to match {self} pattern with value {value}"
            )
        return match
