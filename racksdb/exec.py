# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import sys
import logging
from itertools import chain

from pathlib import Path

from .version import get_version
from .generic.errors import DBFormatError, DBSchemaError
from .generic.db import (
    DBSplittedFilesLoader,
    DBDictsLoader,
    DBStdinLoader,
)
from .generic.dumpers import DBDumperFactory, SchemaDumperFactory
from . import RacksDB
from .drawers import InfrastructureDrawer, RoomDrawer
from .drawers.parameters import DrawingParameters
from .errors import RacksDBError
from .views import RacksDBViews

logger = logging.getLogger(__name__)


class RacksDBExec:
    DEFAULT_FORMAT = "yaml"

    @classmethod
    def run(cls):
        cls()

    def __init__(self):
        parser = argparse.ArgumentParser(description="Do something with RacksDB.")
        parser.add_argument(
            "-v",
            "--version",
            dest="version",
            action="version",
            version="RacksDB " + get_version(),
        )
        parser.add_argument(
            "--debug",
            dest="debug",
            action="store_true",
            help="Enable debug mode",
        )

        parser.add_argument(
            "-s",
            "--schema",
            help="Schema to load (default: %(default)s)",
            default=RacksDB.DEFAULT_SCHEMA,
            type=Path,
        )
        parser.add_argument(
            "-e",
            "--ext",
            help="Path to extensions of schema (default: %(default)s)",
            default=RacksDB.DEFAULT_EXT,
            type=Path,
        )
        parser.add_argument(
            "-b",
            "--db",
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
                help="Action to perform with database",
                dest="action",
                required=True,
            )
        else:
            subparsers = parser.add_subparsers(
                help="Action to perform with database", dest="action"
            )

        # Parser for the schema command
        parser_schema = subparsers.add_parser("schema", help="Dump loaded schema")
        parser_schema.set_defaults(func=self._run_schema)

        # Parser for the dump command
        parser_dump = subparsers.add_parser("dump", help="Dump raw loaded DB")
        parser_dump.set_defaults(func=self._run_dump)

        self.views = RacksDBViews()

        # Generate subcommands for all declared views (converted to actions) and
        # all declared actions with their parameters.
        for action in chain(self.views.views_actions(), self.views.actions()):
            subparser = subparsers.add_parser(action.name, help=action.description)
            for parameter in action.parameters:
                if parameter.specific is not None and parameter.specific != "cli":
                    continue
                if parameter.positional:
                    args = (parameter.name,)
                else:
                    args = [f"--{parameter.name.replace('_','-')}"]
                    if parameter.short is not None:
                        args.insert(0, f"-{parameter.short}")

                kwargs = {"help": parameter.description}
                if parameter.nargs == 0:
                    kwargs["action"] = "store_true"
                else:
                    kwargs["nargs"] = parameter.nargs
                if parameter.choices is not None:
                    kwargs["choices"] = parameter.choices
                if parameter.default is not None:
                    kwargs["default"] = parameter.default
                    if parameter.default_in_help:
                        kwargs["help"] += " (default: %(default)s)"
                if parameter.const is not None:
                    kwargs["const"] = parameter.const
                if parameter.required:
                    kwargs["required"] = True
                if parameter.type:
                    kwargs["type"] = parameter.type
                subparser.add_argument(*args, **kwargs)
                subparser.set_defaults(func=getattr(self, f"_run_{action.name}"))

        self.args = parser.parse_args()

        self._setup_logger()

        try:
            self.db = RacksDB.load(self.args.schema, self.args.ext, self.args.db)
        except DBSchemaError as err:
            logger.error("Error while loading schema: %s", err)
            sys.exit(1)
        except DBFormatError as err:
            logger.error("Error while loading db: %s", err)
            sys.exit(1)

        if not hasattr(self.args, "func"):
            parser.print_usage()
            logger.error("The action argument must be given")
            sys.exit(1)
        try:
            self.args.func()
        except RacksDBError as err:
            logger.critical(err)
            sys.exit(1)

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
        print(SchemaDumperFactory.get("yaml")().dump(self.db._schema))

    def _run_dump(self):
        print(DBDumperFactory.get("yaml")().dump(self.db._loader.content))

    def _run_racks(self):
        self._dump_view()

    def _run_datacenters(self):
        self._dump_view()

    def _run_nodes(self):
        self._dump_view()

    def _run_infrastructures(self):
        self._dump_view()

    def _dump_view(self):
        data = getattr(self.db, self.args.action)
        view = self.views[self.args.action]
        # Filter data with optional filters specified in arguments
        data = data.filter(
            **{
                _filter.name: getattr(self.args, _filter.name)
                for _filter in view.filters
            }
        )

        # Select only the item names
        if self.args.list:
            # When list option is select and no output format is specified, select the
            # console dumper by default.
            if self.args.format is None:
                self.args.format = "console"
            data = [item.name for item in data]

        # If the output format is not defined at this stage, fallback to default.
        if self.args.format is None:
            self.args.format = self.DEFAULT_FORMAT

        print(
            DBDumperFactory.get(self.args.format)(
                show_types=self.args.with_objects_types,
                objects_map=view.objects_map,
                fold=self.args.fold,
            ).dump(data)
        )

    def _run_draw(self):
        file = f"{self.args.name}.{self.args.format}"

        # Handle coordinates opts
        if self.args.coordinates is False:
            coordinates_file = None
        elif self.args.coordinates is True:
            coordinates_file = f"coordinates.{self.args.coordinates_format}"
        else:
            coordinates_file = self.args.coordinates
        coordinates_fh = (
            open(coordinates_file, "w+") if coordinates_file is not None else None
        )
        try:
            if self.args.parameters is None:
                db_loader = DBDictsLoader()
            elif isinstance(self.args.parameters, str):
                if self.args.parameters == "-":
                    db_loader = DBStdinLoader()
                else:
                    db_loader = DBSplittedFilesLoader(Path(self.args.parameters))
            parameters = DrawingParameters.load(db_loader, self.args.drawings_schema)
        except DBSchemaError as err:
            logger.critical("Unable to load drawing parameters schema: %s", str(err))
            sys.exit(1)
        except DBFormatError as err:
            logger.critical("Unable to load drawing parameters: %s", str(err))
            sys.exit(1)
        if self.args.entity == "infrastructure":
            drawer = InfrastructureDrawer(
                self.db,
                self.args.name,
                file,
                self.args.format,
                parameters,
                coordinates_fh,
                self.args.coordinates_format,
            )
        elif self.args.entity == "room":
            drawer = RoomDrawer(
                self.db,
                self.args.name,
                file,
                self.args.format,
                parameters,
                coordinates_fh,
                self.args.coordinates_format,
            )
        drawer.draw()
        logger.info("Generated image file %s", file)
        if self.args.coordinates:
            logger.info("Generated coordinates file %s", coordinates_file)
            coordinates_fh.close()
