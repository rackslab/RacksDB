# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import unittest

from racksdb.generic.openapi import OpenAPIGenerator

from .lib.views import TestDBViews
from .lib.common import valid_schema


class TestDBViewSet(unittest.TestCase):
    def test_generator(self):
        generator = OpenAPIGenerator(
            "Test", "1.0", {"Test": valid_schema()}, TestDBViews()
        )
        generator.generate()
