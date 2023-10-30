# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeBits(SchemaDefinedType):

    pattern = r"(\d+(.\d+)?)(Tb|Gb|Mb)"
    native = int

    def parse(self, value):
        match = self._match(value)
        quantity = float(match.group(1))
        unit = match.group(3)
        if unit == "Mb":
            quantity *= 10 ** 6
        elif unit == "Gb":
            quantity *= 10 ** 9
        elif unit == "Tb":
            quantity *= 10 ** 12
        return int(quantity)
