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
import logging

from .version import __version__
from .generic.errors import DBFormatError, DBSchemaError
from .generic.schema import Schema, SchemaFileLoader, SchemaDefinedTypeLoader
from .generic.db import GenericDB, DBFileLoader
from .generic.dumper import DBDumper

logger = logging.getLogger(__name__)


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
        subparsers = parser.add_subparsers(
            help='Action to perform with database', dest='action'
        )

        # Parser for the datacenters command
        parser_datacenters = subparsers.add_parser(
            'datacenters', help='Get informations about datacenters'
        )
        parser_datacenters.add_argument(
            '-d',
            '--details',
            help='Show datacenters full details',
            action='store_true',
        )
        parser_datacenters.add_argument(
            '--expand',
            help='Expand racks in rows',
            action='store_true',
        )
        parser_datacenters.set_defaults(func=self._run_datacenters)

        # Parser for the groups command
        parser_groups = subparsers.add_parser(
            'groups', help='Get informations about equipments groups'
        )
        parser_groups.add_argument(
            '-d',
            '--details',
            help='Show groups full details',
            action='store_true',
        )
        parser_groups.add_argument(
            '--expand',
            help='Expand equipments in groups',
            action='store_true',
        )

        parser_groups.set_defaults(func=self._run_groups)

        self.args = parser.parse_args()

        self._setup_logger()

        self.schema = None
        self.db = None
        self._load()

        self.args.func()

    def _setup_logger(self):
        if self.args.debug:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO

        root_logger = logging.getLogger()
        root_logger.setLevel(logging_level)
        handler = logging.StreamHandler()
        handler.setLevel(logging_level)
        formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    def _load(self):

        try:
            self.schema = Schema(
                SchemaFileLoader(self.args.schema),
                SchemaDefinedTypeLoader('racksdb.types'),
            )
        except DBSchemaError as err:
            logger.error("Error while loading schema: %s", err)
            sys.exit(1)

        try:
            loader = DBFileLoader(self.args.db)
            self.db = GenericDB('RacksDB', self.schema)
            self.db.load(loader)
        except DBFormatError as err:
            logger.error("Error while loading db: %s", err)
            sys.exit(1)

    def _run_datacenters(self):
        # print list of datacenters
        if not self.args.details:
            for datacenter in self.db.datacenters:
                print(datacenter.name)
                return
        dumper = DBDumper(expand=self.args.expand)
        print(dumper.dump([datacenter for datacenter in self.db.datacenters]))

    def _run_groups(self):
        # print list of equipments groups
        if not self.args.details:
            for group in self.db.groups:
                print(group.name)
                return
        objects_map = {
            'RacksDBDatacenter': 'name',
            'RacksDBDatacenterRoom': 'name',
            'RacksDBDatacenterRoomRack': 'name',
        }
        dumper = DBDumper(objects_map=objects_map, expand=self.args.expand)
        print(dumper.dump([group for group in self.db.groups]))
