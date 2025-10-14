# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from .yaml import DBDumperYAML, SchemaDumperYAML
from .json import DBDumperJSON
from .console import DBDumperConsole
from ..errors import DBDumperError


class DBDumperFactory:
    FORMATS = {"yaml": DBDumperYAML, "json": DBDumperJSON, "console": DBDumperConsole}

    @staticmethod
    def get(_format):
        if _format not in DBDumperFactory.FORMATS:
            raise DBDumperError(f"Unsupported DB dump format {_format}")
        return DBDumperFactory.FORMATS[_format]


class SchemaDumperFactory:
    FORMATS = {"yaml": SchemaDumperYAML}

    @staticmethod
    def get(_format):
        if _format not in SchemaDumperFactory.FORMATS:
            raise DBDumperError(f"Unsupported schema dump format {_format}")
        return SchemaDumperFactory.FORMATS[_format]
