# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from racksdb.generic.definedtype import SchemaDefinedType
from racksdb.generic.errors import DBFormatError


class SchemaDefinedTypeAngle(SchemaDefinedType):

    pattern = r"\d+"

    def parse(self, value):
        match = self._match(value)
        degrees = int(match.group(0))
        if degrees < 0 or degrees > 360:
            raise DBFormatError(f"Invalid angle of {degrees} degrees")
        return degrees
