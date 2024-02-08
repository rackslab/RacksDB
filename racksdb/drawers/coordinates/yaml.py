# Copyright (c) 2022-2024 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml

from .base import CoordinatesDumper


class CoordinatesDumperYaml(CoordinatesDumper):
    def __init__(self):
        pass

    def dump(self, coordinates):
        return yaml.dump(
            {key: coordinate._serialized for key, coordinate in coordinates.items()}
        )
