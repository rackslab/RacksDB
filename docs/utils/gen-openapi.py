#!/usr/bin/env python

import os
from pathlib import Path

import yaml

from racksdb import RacksDB
from racksdb.views import RacksDBViews
from racksdb.generic.schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from racksdb.generic.openapi import OpenAPIGenerator


def main():

    current_dir = os.path.dirname(os.path.realpath(__file__))
    racksdb_schema_path = Path(current_dir).joinpath("../../schema/racksdb.yml")
    racksdb_schema = Schema(
        SchemaFileLoader(racksdb_schema_path),
        SchemaDefinedTypeLoader(RacksDB.DEFINED_TYPES_MODULE),
    )
    views = RacksDBViews()
    openapi = OpenAPIGenerator(
        "RacksDB", {"RacksDB": racksdb_schema}, views
    )
    print(yaml.dump(openapi.generate()))


if __name__ == "__main__":
    main()
