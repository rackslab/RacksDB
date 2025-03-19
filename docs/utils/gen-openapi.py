#!/usr/bin/env python

import os
from pathlib import Path

from rfl.build.projectversion import project_version
from racksdb import RacksDB
from racksdb.views import RacksDBViews
from racksdb.generic.schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from racksdb.generic.openapi import OpenAPIGenerator
from racksdb.generic.dumpers import DBDumperFactory
from racksdb.drawers.parameters import DrawingParameters


def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    racksdb_schema_path = Path(current_dir).joinpath("../../schemas/racksdb.yml")
    racksdb_schema = Schema(
        SchemaFileLoader(racksdb_schema_path),
        SchemaDefinedTypeLoader(RacksDB.DEFINED_TYPES_MODULE),
    )
    drawings_schema_path = Path(current_dir).joinpath("../../schemas/drawings.yml")
    drawing_schema = Schema(
        SchemaFileLoader(drawings_schema_path),
        SchemaDefinedTypeLoader(DrawingParameters.DEFINED_TYPES_MODULE),
    )
    views = RacksDBViews()
    openapi = OpenAPIGenerator(
        "RacksDB",
        project_version(),
        {"RacksDB": racksdb_schema, "Drawings": drawing_schema},
        views,
    )
    dumper = DBDumperFactory.get("yaml")()
    print(dumper.dump(openapi.generate()))


if __name__ == "__main__":
    main()
