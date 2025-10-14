# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Union

from ..generic.schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from ..generic.db import GenericDB


class DrawingParameters(GenericDB):
    DEFAULT_SCHEMA = "/usr/share/racksdb/schemas/drawings.yml"
    PREFIX = "DrawingParameters"
    DEFINED_TYPES_MODULE = "racksdb.drawers.dtypes"

    def __init__(self, schema, loader):
        super().__init__(self.PREFIX, schema)
        self._loader = loader

    @classmethod
    def load(
        cls,
        db_loader,
        schema: Union[str, Path, None] = None,
    ):
        # Unfortunately, default values to arguments cannot be used as they are
        # class attributes and the class is not defined yet at this stage at
        # compilation time. As an alternative, the value None is checked at
        # runtime and replaced by values of class attributes.

        if schema is None:
            schema = Path(cls.DEFAULT_SCHEMA)
        elif isinstance(schema, str):
            schema = Path(schema)

        _schema = Schema(
            SchemaFileLoader(schema),
            SchemaDefinedTypeLoader(cls.DEFINED_TYPES_MODULE),
        )
        _db = cls(_schema, db_loader)
        super(cls, _db).load(_db._loader)
        return _db
