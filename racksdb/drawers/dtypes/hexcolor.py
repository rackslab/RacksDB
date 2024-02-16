# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from typing import Tuple

from racksdb.generic.definedtype import SchemaDefinedType


class SchemaDefinedTypeHexcolor(SchemaDefinedType):

    pattern = r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$"
    native = Tuple[float, float, float, float]

    def parse(self, value):
        self._match(value)
        hexrgb = re.findall("[0-9a-fA-F]{2}", value)
        # If optional alpha channel is not defined, set it to 255/ff (ie. fully opaque)
        if len(hexrgb) == 3:
            hexrgb.append("ff")
        rgb = tuple(int(f"0x{_hex}", 16) / 255 for _hex in hexrgb)
        return rgb
