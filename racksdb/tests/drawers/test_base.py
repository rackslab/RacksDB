# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from racksdb.drawers.base import (
    Drawer,
    default_equipment_colorset,
    default_rack_colorset,
)
from racksdb.drawers.parameters import DrawingParameters
from racksdb.generic.db import DBDictsLoader

from ..lib.common import drawing_schema_path


class FakeEquipmentType:
    def __init__(self, id):
        self.id = id


class FakeEquipment:
    def __init__(self, id, tags):
        self.type = FakeEquipmentType(id)
        if tags is not None:
            self.tags = tags


class FakeRackType:
    def __init__(self, id):
        self.id = id


class FakeRack:
    def __init__(self, id, tags):
        self.type = FakeRackType(id)
        if tags is not None:
            self.tags = tags


class TestDrawer(unittest.TestCase):
    def setUp(self):
        try:
            self.drawings_schema_path = drawing_schema_path()
        except FileNotFoundError as err:
            self.skipTest(err)
        parameters_raw = {
            "colors": {
                "equipments": [
                    {"type": "type1", "background": "#112233"},  # (17, 34, 51)
                    {
                        "tags": ["tag1", "tag2"],
                        "border": "#445566",  # (68, 85, 102)
                    },
                ],
                "racks": [
                    {"type": "type1", "frame": "#112233"},  # (17, 34, 51)
                    {
                        "tags": ["tag1", "tag2"],
                        "pane": "#445566",  # (68, 85, 102)
                    },
                ],
            }
        }
        loader = DBDictsLoader(parameters_raw)
        self.parameters = DrawingParameters.load(loader, self.drawings_schema_path)
        self.drawer = Drawer({}, "output", "format", self.parameters, None, "yaml")

    def test_matching_equipment_coloring_rule(self):
        # Load defaults equipment colorset
        defaults = default_equipment_colorset(self.parameters)
        # Equipment with type type1 must match 1st coloring rule.
        self.assertEqual(
            self.drawer._find_equipment_colorset(FakeEquipment("type1", [])).background,
            (17 / 255, 34 / 255, 51 / 255, 1.0),
        )
        # Equipment with another type must not match any defined coloring rule
        # and fallback to default.
        self.assertEqual(
            self.drawer._find_equipment_colorset(FakeEquipment("type2", [])).background,
            defaults.background,
        )
        # Equipment with type != type1 and all tag1 and tag2 must match 2nd coloring
        # rule.
        self.assertEqual(
            self.drawer._find_equipment_colorset(
                FakeEquipment("type2", ["tag1", "tag2"])
            ).border,
            (68 / 255, 85 / 255, 102 / 255, 1.0),
        )
        # Equipment with type != type1 and only part of 2nd coloring rule tags must not
        # match any defined coloring rule and fallback to default.
        self.assertEqual(
            self.drawer._find_equipment_colorset(
                FakeEquipment("type2", ["tag1"])
            ).background,
            defaults.background,
        )
        self.assertEqual(
            self.drawer._find_equipment_colorset(
                FakeEquipment("type2", ["tag2"])
            ).background,
            defaults.background,
        )
        # Equipment with type != type1 and no tags must not match any defined coloring
        # rule and fallback to default.
        self.assertEqual(
            self.drawer._find_equipment_colorset(
                FakeEquipment("type2", None)
            ).background,
            defaults.background,
        )

    def test_matching_rack_coloring_rule(self):
        # Load defaults equipment colorset
        defaults = default_rack_colorset(self.parameters)
        # Rack with type type1 must match 1st coloring rule.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type1", [])).frame,
            (17 / 255, 34 / 255, 51 / 255, 1.0),
        )
        # Rack with another type must not match any defined coloring rule and fallback
        # to default.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", [])).frame,
            defaults.frame,
        )
        # Rack with type != type1 and all tag1 and tag2 must match 2nd coloring rule.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", ["tag1", "tag2"])).pane,
            (68 / 255, 85 / 255, 102 / 255, 1.0),
        )
        # Rack with type != type1 and only part of 2nd coloring rule tags must not match
        # any defined coloring rule and fallback to default.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", ["tag1"])).pane,
            defaults.pane,
        )
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", ["tag2"])).pane,
            defaults.pane,
        )
        # Rack with type != type1 and no tags must not match any defined coloring rule
        # and fallback to default.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", None)).pane,
            defaults.pane,
        )
