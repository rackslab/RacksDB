# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeRackHeight(SchemaDefinedType):
    pattern = r"(\d+)u"
    native = int

    def parse(self, value):
        match = self._match(value)
        return int(match.group(1))
