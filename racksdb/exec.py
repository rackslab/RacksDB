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
            '--with-objects-types',
            help='Show object types in details',
            action='store_true',
        )
        parser_datacenters.add_argument(
            '--expand',
            help='Expand racks in rows',
            action='store_true',
        )
        parser_datacenters.set_defaults(func=self._run_datacenters)

        # Parser for the infrastructures command
        parser_infras = subparsers.add_parser(
            'infrastructures', help='Get informations about infrastructures'
        )
        parser_infras.add_argument(
            '-d',
            '--details',
            help='Show infrastructures full details',
            action='store_true',
        )
        parser_infras.add_argument(
            '--with-objects-types',
            help='Show object types in details',
            action='store_true',
        )
        parser_infras.add_argument(
            '--expand',
            help='Expand equipments in infrastructures',
            action='store_true',
        )
        parser_infras.set_defaults(func=self._run_infras)

        # Parser for the nodes command
        parser_nodes = subparsers.add_parser(
            'nodes', help='Get informations about nodes'
        )
        parser_nodes.add_argument(
            '-d',
            '--details',
            help='Show nodes full details',
            action='store_true',
        )
        parser_nodes.add_argument(
            '--with-objects-types',
            help='Show object types in details',
            action='store_true',
        )
        parser_nodes.add_argument(
            '--expand',
            help='Expand nodes',
            action='store_true',
        )
        parser_nodes.add_argument(
            '--name',
            help='Filter nodes by name',
        )
        parser_nodes.add_argument(
            '--infrastructure',
            help='Filter nodes by infrastructure',
        )
        parser_nodes.add_argument(
            '--tag',
            help='Filter nodes by tag',
        )
        parser_nodes.set_defaults(func=self._run_nodes)

        # Parser for the racks command
        parser_racks = subparsers.add_parser(
            'racks', help='Get informations about racks'
        )
        parser_racks.add_argument(
            '-d',
            '--details',
            help='Show racks full details',
            action='store_true',
        )
        parser_racks.add_argument(
            '--with-objects-types',
            help='Show object types in details',
            action='store_true',
        )
        parser_racks.add_argument(
            '--expand',
            help='Expand racks',
            action='store_true',
        )
        parser_racks.set_defaults(func=self._run_racks)

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
            print(
                '\n'.join(
                    [datacenter.name for datacenter in self.db.datacenters]
                )
            )
            return
        dumper = DBDumper(
            show_types=self.args.with_objects_types, expand=self.args.expand
        )
        print(dumper.dump([datacenter for datacenter in self.db.datacenters]))

    def _run_infras(self):
        # print list of infrastructures
        if not self.args.details:
            print(
                '\n'.join(
                    [
                        infrastructure.name
                        for infrastructure in self.db.infrastructures
                    ]
                )
            )
            return
        objects_map = {
            'RacksDBDatacenter': 'name',
            'RacksDBDatacenterRoom': 'name',
            'RacksDBDatacenterRoomRack': 'name',
        }
        dumper = DBDumper(
            show_types=self.args.with_objects_types,
            objects_map=objects_map,
            expand=self.args.expand,
        )
        print(
            dumper.dump(
                [infrastructure for infrastructure in self.db.infrastructures]
            )
        )

    def _run_nodes(self):

        # add back references on nodes
        for infrastructure in self.db.infrastructures:
            for part in infrastructure.layout:
                for node in part.nodes:
                    node.infrastructure = infrastructure.name
                    node.datacenter = infrastructure.datacenter.name
                    node.room = infrastructure.room.name
                    node.rack = part.rack

        # When users search nodes by name, they expect the nodes being expanded
        # to get one node out of a nodeset.
        if self.args.name is not None:
            self.args.expand = True

        selected_nodes = self.db.find_objects('Node', self.args.expand)

        # filter nodes by name
        if self.args.name is not None:
            selected_nodes = [
                node for node in selected_nodes if self.args.name == node.name
            ]

        # filter nodes by infrastructure
        if self.args.infrastructure is not None:
            selected_nodes = [
                node
                for node in selected_nodes
                if self.args.infrastructure == node.infrastructure
            ]

        # filter nodes by tag
        if self.args.tag is not None:
            selected_nodes = [
                node
                for node in selected_nodes
                if (
                    hasattr(node.rack, 'tags')
                    and self.args.tag in node.rack.tags
                )
                or (hasattr(node, 'tags') and self.args.tag in node.tags)
            ]

        if not self.args.details:
            print('\n'.join([str(node.name) for node in selected_nodes]))
            return
        objects_map = {
            'RacksDBGroupRack': 'name',
        }
        dumper = DBDumper(
            show_types=self.args.with_objects_types,
            objects_map=objects_map,
            expand=self.args.expand,
        )
        print(dumper.dump(selected_nodes))

    def _run_racks(self):

        # add back reference to datacenter/room/row on racks
        for datacenter in self.db.datacenters:
            for room in datacenter.rooms:
                for row in room.rows:
                    for rack in row.racks:
                        rack.row = row
                        rack.room = room
                        rack.datacenter = datacenter

        selected_racks = self.db.find_objects(
            'DatacenterRoomRack', self.args.expand
        )

        # add references to equipments
        for rack in selected_racks:
            for infrastructure in self.db.infrastructures:
                for part in infrastructure.layout:
                    if rack.name == part.rack.name:
                        rack.nodes = part.nodes

        if not self.args.details:
            print('\n'.join([str(rack.name) for rack in selected_racks]))
            return
        objects_map = {
            'RacksDBDatacenter': 'name',
            'RacksDBDatacenterRoom': 'name',
            'RacksDBDatacenterRoomRow': 'name',
            'RacksDBDatacenterRoomRack': 'name',
            'RacksDBNodeType': 'id',
        }
        dumper = DBDumper(
            show_types=self.args.with_objects_types,
            objects_map=objects_map,
            expand=self.args.expand,
        )
        print(dumper.dump(selected_racks))
