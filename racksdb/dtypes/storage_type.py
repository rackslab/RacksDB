# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeStorageType(SchemaDefinedType):

    pattern = r"(ssd|disk|nvme)"
    native = str

    def parse(self, value):
        self._match(value)  # just check it matches
        return value
