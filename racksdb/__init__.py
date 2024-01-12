# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Union

from .generic.schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from .generic.db import GenericDB, DBDict, DBList, DBSplittedFilesLoader
from . import bases


class RacksDB(GenericDB):

    DEFAULT_DB = "/var/lib/racksdb"
    DEFAULT_SCHEMA = "/usr/share/racksdb/schemas/racksdb.yml"
    DEFAULT_EXT = "/etc/racksdb/extensions.yml"
    PREFIX = "RacksDB"
    DEFINED_TYPES_MODULE = "racksdb.dtypes"

    def __init__(self, schema, loader):
        super().__init__(self.PREFIX, schema, bases)
        self._loader = loader

    @property
    def nodes(self):
        result = DBDict()
        for infrastructure in self.infrastructures:
            result.update(infrastructure.nodes)
        return result

    @property
    def racks(self):
        result = DBList()
        for datacenter in self.datacenters:
            for room in datacenter.rooms:
                for row in room.rows:
                    for rack in row.racks:
                        result.append(rack)
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
