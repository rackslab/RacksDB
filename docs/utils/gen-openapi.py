#!/usr/bin/env python

import os
from pathlib import Path

import yaml

from racksdb import RacksDB
from racksdb.views import RacksDBViews
from racksdb.generic.openapi import OpenAPIGenerator


def main():

    current_dir = os.path.dirname(os.path.realpath(__file__))
    schema_path = Path(current_dir).joinpath("../../schema/racksdb.yml")
    db_path = Path(current_dir).joinpath("../../examples/db")
    db = RacksDB.load(db=db_path, schema=schema_path)
    views = RacksDBViews()
    openapi = OpenAPIGenerator(db, views)
    print(yaml.dump(openapi.generate()))


if __name__ == "__main__":
    main()
