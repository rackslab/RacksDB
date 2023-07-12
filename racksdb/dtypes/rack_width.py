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

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeRackWidth(SchemaDefinedType):

    pattern = r"full|(\d+)(/\d+)?"

    def parse(self, value):
        match = self._match(value)
        if value == 'full':
            return 1.0
        else:
            dividend = int(match.group(1))
            divisor = match.group(2)
            if divisor is not None:
                divisor = float(divisor[1:])
            else:
                divisor = 1.0
            return dividend / divisor
