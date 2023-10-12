# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeBytes(SchemaDefinedType):

    pattern = r"(\d+(.\d+)?)(TB|Tb|GB|Gb|MB|Mb)"
    native = int

    def parse(self, value):
        match = self._match(value)
        quantity = float(match.group(1))
        unit = match.group(3)
        if unit == "Mb":
            quantity *= (10 ** 6) / 8
        elif unit == "MB":
            quantity *= 1024 ** 2
        elif unit == "Gb":
            quantity *= (10 ** 9) / 8
        elif unit == "GB":
            quantity *= 1024 ** 3
        elif unit == "Tb":
            quantity *= (10 ** 12) / 8
        elif unit == "TB":
            quantity *= 1024 ** 4
        return int(quantity)
