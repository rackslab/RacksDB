# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeDimension(SchemaDefinedType):

    pattern = r"(\d+(.\d+)?)(mm|cm|m)"

    def parse(self, value):
        match = self._match(value)
        size = float(match.group(1))
        unit = match.group(3)
        if unit == "cm":
            size *= 10
        elif unit == "m":
            size *= 1000
        return int(size)
