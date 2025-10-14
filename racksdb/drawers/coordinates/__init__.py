# Copyright (c) 2022-2024 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from .json import CoordinatesDumperJson
from .yaml import CoordinatesDumperYaml


class CoordinateDumperFactory:
    FORMATS = {"json": CoordinatesDumperJson, "yaml": CoordinatesDumperYaml}

    @staticmethod
    def create(format: str):
        assert format in CoordinateDumperFactory.FORMATS.keys()
        return CoordinateDumperFactory.FORMATS[format]()
