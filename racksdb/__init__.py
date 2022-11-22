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
from typing import Union

from .generic.schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from .generic.db import GenericDB, DBList, DBFileLoader, DBSplittedFilesLoader
from . import bases


class RacksDB(GenericDB):

    DEFAULT_DB = '/var/lib/racksdb'
    DEFAULT_SCHEMA = '/usr/share/racksdb/schema.yml'
    DEFAULT_EXT = '/etc/racksdb/extensions.yml'
    PREFIX = 'RacksDB'
    DEFINED_TYPES_MODULE = 'racksdb.types'

    def __init__(self, schema, loader):
        super().__init__(self.PREFIX, schema, bases)
        self._loader = loader

    @property
    def nodes(self):
        result = DBList([])
        for infrastructure in self.infrastructures:
            result += infrastructure.nodes
        return result

    @classmethod
    def load(
        cls,
        schema: Union[str, Path, None] = None,
        ext: Union[str, Path, None] = None,
        db: Union[str, Path, None] = None,
    ):
        # Unfortunately, default values to arguments cannot be used as they are
        # class attributes and the class is not defined yet at this stage at
        # compilation time. As an alternative, the value None is checked at
        # runtime and replaced by values of class attributes.

        if schema is None:
            schema = Path(cls.DEFAULT_SCHEMA)
        elif isinstance(schema, str):
            schema = Path(schema)
        if ext is None:
            ext = Path(cls.DEFAULT_EXT)
        elif isinstance(ext, str):
            ext = Path(ext)
        if db is None:
            db = Path(cls.DEFAULT_DB)
        elif isinstance(db, str):
            db = Path(db)
        _schema = Schema(
            SchemaFileLoader(schema, ext),
            SchemaDefinedTypeLoader(cls.DEFINED_TYPES_MODULE),
        )
        _db = cls(_schema, DBSplittedFilesLoader(db))
        super(cls, _db).load(_db._loader)
        return _db
