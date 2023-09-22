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
import sys
import logging
from pathlib import Path

from .version import get_version
from .generic.errors import DBFormatError, DBSchemaError
from .generic.dumper import DBDumper, SchemaDumper
from . import RacksDB
from .drawers import InfrastructureDrawer, RoomDrawer

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
            version='RacksDB ' + get_version(),
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
            help="Schema to load (default: %(default)s)",
            default=RacksDB.DEFAULT_SCHEMA,
            type=Path,
        )
        parser.add_argument(
            '-e',
            '--ext',
            help="Path to extensions of schema (default: %(default)s)",
            default=RacksDB.DEFAULT_EXT,
            type=Path,
        )
        parser.add_argument(
            '-b',
            '--db',
            help="Database to load (default: %(default)s)",
            default=RacksDB.DEFAULT_DB,
            type=Path,
        )

        # Unfortunately, Python 3.6 does support add_subparsers() required
        # attribute. The requirement is later handled with hasattr() check on
        # args.func to provide the same functionnal level.
        # This Python version conditionnal test can be removed when support of
        # Python 3.6 is dropped in RacksDB.
        if sys.version_info[1] >= 3 and sys.version_info[1] >= 7:
            subparsers = parser.add_subparsers(
                help='Action to perform with database',
                dest='action',
                required=True,
            )
        else:
            subparsers = parser.add_subparsers(
                help='Action to perform with database', dest='action'
            )

        # Parser for the schema command
        parser_schema = subparsers.add_parser(
            'schema', help='Dump loaded schema'
        )
        parser_schema.set_defaults(func=self._run_schema)

        # Parser for the dump command
        parser_dump = subparsers.add_parser('dump', help='Dump raw loaded DB')
        parser_dump.set_defaults(func=self._run_dump)

        # Parser for the datacenters command
        parser_datacenters = subparsers.add_parser(
            'datacenters', help='Get informations about datacenters'
        )
        parser_datacenters.add_argument(
            '-l',
            '--list',
            help='List datacenters',
            action='store_true',
        )
        parser_datacenters.add_argument(
            '--with-objects-types',
            help='Show object types in dumps',
            action='store_true',
        )
        parser_datacenters.add_argument(
            '--name',
            help='Filter datacenter by name',
        )
        parser_datacenters.add_argument(
            '--tags', help='Filter datacenter by tag', nargs='*'
        )
        parser_datacenters.set_defaults(func=self._run_datacenters)

        # Parser for the infrastructures command
        parser_infras = subparsers.add_parser(
            'infrastructures', help='Get informations about infrastructures'
        )
        parser_infras.add_argument(
            '-l',
            '--list',
            help='List infrastructures names',
            action='store_true',
        )
        parser_infras.add_argument(
            '--with-objects-types',
            help='Show object types in dumps',
            action='store_true',
        )
        parser_infras.add_argument(
            '--name',
            help='Filter infrastructures by name',
        )
        parser_infras.add_argument(
            '--tags', help='Filter infrastructures by tag', nargs='*'
        )
        parser_infras.set_defaults(func=self._run_infras)

        # Parser for the nodes command
        parser_nodes = subparsers.add_parser(
            'nodes', help='Get informations about nodes'
        )
        parser_nodes.add_argument(
            '-l',
            '--list',
            help='List nodes names',
            action='store_true',
        )
        parser_nodes.add_argument(
            '--with-objects-types',
            help='Show object types in dumps',
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
            '--tags', help='Filter nodes by tag', nargs='*'
        )
        parser_nodes.set_defaults(func=self._run_nodes)

        # Parser for the racks command
        parser_racks = subparsers.add_parser(
            'racks', help='Get informations about racks'
        )
        parser_racks.add_argument(
            '-l',
            '--list',
            help='List racks names',
            action='store_true',
        )
        parser_racks.add_argument(
            '--with-objects-types',
            help='Show object types in dumps',
            action='store_true',
        )
        parser_racks.add_argument(
            '--name',
            help='Filter racks by name',
        )

        parser_racks.set_defaults(func=self._run_racks)

        # Parser for the draw command
        parser_draw = subparsers.add_parser('draw', help='Draw DB components')
        parser_draw.add_argument(
            'entity',
            choices=['room', 'infrastructure'],
            help='Entity to draw',
        )
        parser_draw.add_argument(
            '--name',
            help='Name of entity to draw',
            required=True,
        )
        parser_draw.add_argument(
            '--format',
            help='Format of output image (default: %(default)s)',
            choices=['png', 'svg', 'pdf'],
            default='png',
        )
        parser_draw.set_defaults(func=self._run_draw)

        self.args = parser.parse_args()

        self._setup_logger()

        try:
            self.db = RacksDB.load(
                self.args.schema, self.args.ext, self.args.db
            )
        except DBSchemaError as err:
            logger.error("Error while loading schema: %s", err)
            sys.exit(1)
        except DBFormatError as err:
            logger.error("Error while loading db: %s", err)
            sys.exit(1)

        if not hasattr(self.args, 'func'):
            parser.print_usage()
            logger.error("The action argument must be given")
            sys.exit(1)

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

    def _run_schema(self):
        print(
            SchemaDumper().dump(self.db._schema),
            end='',
        )

    def _run_dump(self):
        print(
            DBDumper().dump(self.db._loader.content),
            end='',
        )

    def _run_datacenters(self):
        selected_datacenters = self.db.datacenters.filter(
            name=self.args.name,
            tags=self.args.tags,
        )
        # print list of datacenters
        if self.args.list:
            print(
                '\n'.join(
                    [datacenter.name for datacenter in selected_datacenters]
                )
            )
            return
        objects_map = {
            'RacksDBDatacenter': None,
            'RacksDBDatacenterRoom': 'name',
            'RacksDBDatacenterRoomRow': 'name',
            'RacksDBDatacenterRoomRack': 'name',
        }
        dumper = DBDumper(
            show_types=self.args.with_objects_types,
            objects_map=objects_map,
        )
        print(
            dumper.dump([datacenter for datacenter in selected_datacenters]),
            end='',
        )

    def _run_infras(self):
        selected_infras = self.db.infrastructures.filter(
            name=self.args.name,
            tags=self.args.tags,
        )

        # print list of infrastructures
        if self.args.list:
            print(
                '\n'.join(
                    [infrastructure.name for infrastructure in selected_infras]
                )
            )
            return
        objects_map = {
            'RacksDBDatacenter': 'name',
            'RacksDBDatacenterRoom': 'name',
            'RacksDBDatacenterRoomRack': 'name',
            'RacksDBInfrastructure': None,
        }
        dumper = DBDumper(
            show_types=self.args.with_objects_types,
            objects_map=objects_map,
        )
        print(
            dumper.dump([infrastructure for infrastructure in selected_infras]),
            end='',
        )

    def _run_nodes(self):

        selected_nodes = self.db.nodes.filter(
            name=self.args.name,
            infrastructure=self.args.infrastructure,
            tags=self.args.tags,
        )

        if self.args.list:
            print('\n'.join([str(node.name) for node in selected_nodes]))
            return
        objects_map = {
            'RacksDBGroupRack': 'name',
            'RacksDBDatacenter': 'name',
            'RacksDBDatacenterRoom': 'name',
            'RacksDBDatacenterRoomRow': 'name',
            'RacksDBInfrastructure': 'name',
        }
        dumper = DBDumper(
            show_types=self.args.with_objects_types,
            objects_map=objects_map,
        )
        print(dumper.dump(selected_nodes), end='')

    def _run_racks(self):

        selected_racks = self.db.find_objects('DatacenterRoomRack', True)

        # filter racks by name
        if self.args.name is not None:
            selected_racks = [
                rack for rack in selected_racks if self.args.name == rack.name
            ]

        # add references to equipments
        for rack in selected_racks:
            for infrastructure in self.db.infrastructures:
                for part in infrastructure.layout:
                    if rack.name == part.rack.name:
                        rack.nodes = part.nodes

        if self.args.list:
            print('\n'.join([str(rack.name) for rack in selected_racks]))
            return
        objects_map = {
            'RacksDBDatacenter': 'name',
            'RacksDBDatacenterRoom': 'name',
            'RacksDBDatacenterRoomRow': 'name',
            'RacksDBDatacenterRoomRack': None,
            'RacksDBNodeType': 'id',
            'RacksDBInfrastructure': 'name',
        }
        dumper = DBDumper(
            show_types=self.args.with_objects_types,
            objects_map=objects_map,
        )
        print(dumper.dump(selected_racks), end='')

    def _run_draw(self):
        if self.args.entity == 'infrastructure':
            drawer = InfrastructureDrawer(
                self.db, self.args.name, self.args.format
            )
        elif self.args.entity == 'room':
            drawer = RoomDrawer(self.db, self.args.name, self.args.format)
        drawer.draw()
