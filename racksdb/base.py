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

from .generic.schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from .generic.db import GenericDB, DBFileLoader


class RacksDB(GenericDB):

    PREFIX = 'RacksDB'
    DEFINED_TYPES_MODULE = 'racksdb.types'

    def __init__(self, schema):
        super().__init__(self.PREFIX, schema)

    @classmethod
    def load(cls, schema_path, db_path):
        schema = Schema(
            SchemaFileLoader(schema_path),
            SchemaDefinedTypeLoader(cls.DEFINED_TYPES_MODULE),
        )
        db = cls(schema)
        super(cls, db).load(DBFileLoader(db_path))
        return db
