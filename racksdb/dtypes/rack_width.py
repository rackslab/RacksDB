# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeRackWidth(SchemaDefinedType):

    pattern = r"full|(\d+)(/\d+)?"

    def parse(self, value):
        match = self._match(value)
        if value == "full":
            return 1.0
        else:
            dividend = int(match.group(1))
            divisor = match.group(2)
            if divisor is not None:
                divisor = float(divisor[1:])
            else:
                divisor = 1.0
            return dividend / divisor
