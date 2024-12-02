# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeWatts(SchemaDefinedType):

    pattern = r"(\d+(.\d+)?)(W|kW|MW)"
    native = int

    def parse(self, value):
        match = self._match(value)
        quantity = float(match.group(1))
        unit = match.group(3)
        if unit == "kW":
            quantity *= 10**3
        elif unit == "MW":
            quantity *= 10**6
        return int(quantity)
