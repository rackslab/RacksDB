# Copyright (c) 2022-2024 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import json

from .base import CoordinatesDumper


class CoordinatesDumperJson(CoordinatesDumper):
    def __init__(self):
        pass

    def dump(self, coordinates):
        return json.dumps(
            {key: coordinate._serialized for key, coordinate in coordinates.items()}
        )
