# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeBytes(SchemaDefinedType):
    pattern = r"(\d+(.\d+)?)(TB|GB|MB)"
    native = int

    def parse(self, value):
        match = self._match(value)
        quantity = float(match.group(1))
        unit = match.group(3)
        if unit == "MB":
            quantity *= 1024**2
        elif unit == "GB":
            quantity *= 1024**3
        elif unit == "TB":
            quantity *= 1024**4
        return int(quantity)
