# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import unittest
from pathlib import Path

from racksdb.drawers.base import Drawer, DefaultEquipmentColorSet, DefaultRackColorSet
from racksdb.drawers.parameters import DrawingParameters
from racksdb.generic.db import DBEmptyLoader


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
        # Try relative path and system paths sequentially for both the schema
        # and example database. If none of these paths exist, gently skip the
        # test with meaningful message.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        drawings_schema_paths = [
            Path(current_dir).joinpath("../../schemas/drawings.yml"),
            Path("/usr/share/racksdb/drawings.yml"),
        ]
        self.drawings_schema_path = None
        for drawings_schema_path in drawings_schema_paths:
            if drawings_schema_path.exists():
                self.drawings_schema_path = drawings_schema_path
                break
        if self.drawings_schema_path is None:
            self.skipTest("Unable to find drawings schema file to run test")
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
        loader = DBEmptyLoader(parameters_raw)
        parameters = DrawingParameters.load(loader, self.drawings_schema_path)
        self.drawer = Drawer({}, "output", "format", parameters)

    def test_matching_equipment_coloring_rule(self):
        # Equipment with type type1 must match 1st coloring rule.
        self.assertEqual(
            self.drawer._find_equipment_colorset(FakeEquipment("type1", [])).background,
            (17 / 255, 34 / 255, 51 / 255),
        )
        # Equipment with another type must not match any defined coloring rule
        # and fallback to default.
        self.assertEqual(
            self.drawer._find_equipment_colorset(FakeEquipment("type2", [])).background,
            DefaultEquipmentColorSet.background,
        )
        # Equipment with type != type1 and all tag1 and tag2 must match 2nd coloring
        # rule.
        self.assertEqual(
            self.drawer._find_equipment_colorset(
                FakeEquipment("type2", ["tag1", "tag2"])
            ).border,
            (68 / 255, 85 / 255, 102 / 255),
        )
        # Equipment with type != type1 and only part of 2nd coloring rule tags must not
        # match any defined coloring rule and fallback to default.
        self.assertEqual(
            self.drawer._find_equipment_colorset(
                FakeEquipment("type2", ["tag1"])
            ).background,
            DefaultEquipmentColorSet.background,
        )
        self.assertEqual(
            self.drawer._find_equipment_colorset(
                FakeEquipment("type2", ["tag2"])
            ).background,
            DefaultEquipmentColorSet.background,
        )
        # Equipment with type != type1 and no tags must not match any defined coloring
        # rule and fallback to default.
        self.assertEqual(
            self.drawer._find_equipment_colorset(
                FakeEquipment("type2", None)
            ).background,
            DefaultEquipmentColorSet.background,
        )

    def test_matching_rack_coloring_rule(self):
        # Rack with type type1 must match 1st coloring rule.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type1", [])).frame,
            (17 / 255, 34 / 255, 51 / 255),
        )
        # Rack with another type must not match any defined coloring rule and fallback
        # to default.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", [])).frame,
            DefaultRackColorSet.frame,
        )
        # Rack with type != type1 and all tag1 and tag2 must match 2nd coloring rule.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", ["tag1", "tag2"])).pane,
            (68 / 255, 85 / 255, 102 / 255),
        )
        # Rack with type != type1 and only part of 2nd coloring rule tags must not match
        # any defined coloring rule and fallback to default.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", ["tag1"])).pane,
            DefaultRackColorSet.pane,
        )
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", ["tag2"])).pane,
            DefaultRackColorSet.pane,
        )
        # Rack with type != type1 and no tags must not match any defined coloring rule
        # and fallback to default.
        self.assertEqual(
            self.drawer._find_rack_colorset(FakeRack("type2", None)).pane,
            DefaultRackColorSet.pane,
        )
