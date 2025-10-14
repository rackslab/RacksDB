# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import re

from .errors import DBFormatError


class SchemaDefinedType:
    def __init__(self):
        self.name = self.__class__.__module__

    def __str__(self):
        return f"~{self.name}"

    def _match(self, value):
        regex = re.compile(self.pattern)
        match = regex.match(str(value))
        if match is None:
            raise DBFormatError(f"Unable to match {self} pattern with value {value}")
        return match
