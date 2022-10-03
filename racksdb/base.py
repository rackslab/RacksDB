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

from pathlib import Path

from .generic.schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from .generic.db import GenericDB, DBFileLoader, DBSplittedFilesLoader


class RacksDB(GenericDB):

    DEFAULT_DB = '/var/lib/racksdb'
    DEFAULT_SCHEMA = '/usr/share/racksdb/schema.yml'
    DEFAULT_EXT = '/etc/racksdb/extensions.yml'
    PREFIX = 'RacksDB'
    DEFINED_TYPES_MODULE = 'racksdb.types'

    def __init__(self, schema, loader):
        super().__init__(self.PREFIX, schema)
        self._loader = loader

    @classmethod
    def load(
        cls,
        schema_path: Path = None,
        ext_path: Path = None,
        db_path: Path = None,
    ):
        # Unfortunately, default values to arguments cannot be used as they are
        # class attributes and the class is not defined yet at this stage at
        # compilation time. As an alternative, the value None is checked at
        # runtime and replaced by values of class attributes.
        if schema_path is None:
            schema_path = Path(cls.DEFAULT_SCHEMA)
        if ext_path is None:
            ext_path = Path(cls.DEFAULT_EXT)
        if db_path is None:
            db_path = Path(cls.DEFAULT_DB)
        schema = Schema(
            SchemaFileLoader(schema_path, ext_path),
            SchemaDefinedTypeLoader(cls.DEFINED_TYPES_MODULE),
        )
        db = cls(schema, DBSplittedFilesLoader(db_path))
        super(cls, db).load(db._loader)
        return db
