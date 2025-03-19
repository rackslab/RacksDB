# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
import typing as t

from .generic.schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from .generic.db import GenericDB, DBDict, DBList, DBSplittedFilesLoader
from .generic.errors import DBSchemaError, DBFormatError
from .errors import (
    RacksDBFormatError,
    RacksDBSchemaError,
    RacksDBRequestError,
    RacksDBNotFoundError,
)
from . import bases


class RacksDB(GenericDB):
    DEFAULT_DB = "/var/lib/racksdb"
    DEFAULT_SCHEMA = "/usr/share/racksdb/schemas/racksdb.yml"
    DEFAULT_EXT = "/etc/racksdb/extensions.yml"
    DEFAULT_UI = "/usr/share/racksdb/frontend"
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

    def tags(
        self,
        node: t.Optional[str] = None,
        infrastructure: t.Optional[str] = None,
        datacenter: t.Optional[str] = None,
        on_nodes: bool = False,
        on_racks: bool = False,
    ) -> DBList:
        if not node and not infrastructure and not datacenter:
            raise RacksDBRequestError(
                "Either node, infrastructure or datacenter parameter must be defined "
                "to retrieve tags"
            )

        if node:
            nodes = self.nodes.filter(name=node)
            if node not in nodes:
                raise RacksDBNotFoundError(f"Unable to find node {node}")
            return nodes[node].tags
        elif infrastructure:
            if infrastructure not in self.infrastructures:
                raise RacksDBNotFoundError(
                    f"Unable to find infrastructure {infrastructure}"
                )
            if on_nodes:
                return self.infrastructures[infrastructure].nodes_tags
            else:
                return getattr(self.infrastructures[infrastructure], "tags", [])
        elif datacenter:
            if datacenter not in self.datacenters:
                raise RacksDBNotFoundError(f"Unable to find datacenter {datacenter}")
            if on_racks:
                return self.datacenters[datacenter].racks_tags
            else:
                return self.datacenters[datacenter].tags

    @classmethod
    def load(
        cls,
        schema: t.Union[str, Path, None] = None,
        ext: t.Union[str, Path, None] = None,
        db: t.Union[str, Path, None] = None,
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
        try:
            _schema = Schema(
                SchemaFileLoader(schema, ext),
                SchemaDefinedTypeLoader(cls.DEFINED_TYPES_MODULE),
            )
        except DBSchemaError as err:
            raise RacksDBSchemaError(str(err)) from err
        try:
            _db = cls(_schema, DBSplittedFilesLoader(db))
            super(cls, _db).load(_db._loader)
        except DBFormatError as err:
            raise RacksDBFormatError(str(err)) from err
        return _db
