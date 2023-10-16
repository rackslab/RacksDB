# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import sys
import logging
from pathlib import Path

from .version import get_version
from .generic.errors import DBFormatError, DBSchemaError
from .generic.dumpers import DBDumperFactory, SchemaDumperFactory
from . import RacksDB
from .drawers import InfrastructureDrawer, RoomDrawer
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

        for view in self.views:
            subparser = subparsers.add_parser(view.content, help=view.description)
            for parameter in self.views.parameters():
                args = [f"--{parameter.name.replace('_','-')}"]
                if parameter.short is not None:
                    args.insert(0, f"-{parameter.short}")
                kwargs = {
                    "help": parameter.description,
                }
                if parameter.type is None:
                    kwargs["action"] = "store_true"
                if parameter.default is not None:
                    kwargs["default"] = parameter.default
                    kwargs["help"] += " (default: %(default)s)"
                if parameter.choices is not None:
                    kwargs["choices"] = parameter.choices
                subparser.add_argument(*args, **kwargs)
            for _filter in view.filters:
                subparser.add_argument(
                    f"--{_filter.name}",
                    help=_filter.description,
                    nargs=_filter.nargs,
                )
            subparser.set_defaults(func=self._dump_view)

        # Parser for the draw command
        for action in self.views.actions():
            subparser = subparsers.add_parser(action.name, help=action.description)
            for arg in action.args:
                if arg.positional:
                    args = (arg.name,)
                else:
                    args = (f"--{arg.name}",)
                kwargs = {"help": arg.description}
                if arg.choices is not None:
                    kwargs["choices"] = arg.choices
                if arg.default is not None:
                    kwargs["default"] = arg.default
                    kwargs["help"] += " (default: %(default)s)"
                if arg.required:
                    kwargs["required"] = True
                subparser.add_argument(*args, **kwargs)
                subparser.set_defaults(func=self._run_action)

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

    def _run_action(self):
        if self.args.action == "draw":
            self._run_draw()
        else:
            raise RacksDBError(f"Unsupported action {self.args.action}")

    def _run_draw(self):
        file = f"{self.args.name}.{self.args.format}"
        if self.args.entity == "infrastructure":
            drawer = InfrastructureDrawer(
                self.db, self.args.name, file, self.args.format
            )
        elif self.args.entity == "room":
            drawer = RoomDrawer(self.db, self.args.name, file, self.args.format)
        drawer.draw()
        logger.info("Generated image file %s", file)
