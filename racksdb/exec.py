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

import argparse
import yaml
import sys

from .version import __version__
from .errors import RacksDBFormatError, RacksDBSchemaError
from .schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from .db import GenericDB, DBFileLoader


class RacksDBExec:
    @classmethod
    def run(cls):
        cls()

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Do something with RacksDB.'
        )
        parser.add_argument(
            '-v',
            '--version',
            dest='version',
            action='version',
            version='RacksDB ' + __version__,
        )
        parser.add_argument(
            '--debug',
            dest='debug',
            action='store_true',
            help="Enable debug mode",
        )

        parser.add_argument(
            '-s',
            '--schema',
            help="Schema to load",
            required=True,
        )
        parser.add_argument(
            '-b',
            '--db',
            help="Database to load",
            required=True,
        )

        self.args = parser.parse_args()
        self._run()

    def _run(self):

        try:
            schema = Schema(
                SchemaFileLoader(self.args.schema),
                SchemaDefinedTypeLoader('racksdb.types'),
            )
        except RacksDBSchemaError as err:
            print(f"Error while loading schema: {err}")
            sys.exit(1)
        schema.dump()

        try:
            loader = DBFileLoader(self.args.db)
            db = GenericDB('RacksDB', schema)
            db.load(loader)
        except RacksDBFormatError as err:
            print(f"Error while loading db: {err}")
            sys.exit(1)

        db.dump()
