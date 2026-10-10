# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import base64
import io
import json
import math
import tempfile
import unittest
from pathlib import Path

from racksdb import RacksDB
from racksdb.drawers.base import find_equipment_colorset
from racksdb.drawers.gltf import (
    EQUIPMENT_BACK_INSET_M,
    EQUIPMENT_SIDE_CLEARANCE_M,
    FLOOR_TILE_M,
    FLOOR_TILE_PERFORATED_PNG,
    FLOOR_TILE_SOLID_PNG,
    GHOST_EQUIPMENT_ALPHA,
    GltfInfrastructureDrawer,
    ROOM_GAP_M,
)
from racksdb.drawers.infrastructure import InfrastructureDrawer
from racksdb.drawers.layout import rack_slot_offset_x
from racksdb.drawers.parameters import DrawingParameters
from racksdb.drawers.room import RoomDrawer
from racksdb.generic.db import DBDictsLoader

from ..lib.common import drawing_schema_path, schema_path, db_path


def _load_gltf(name, parameters=None):
    db = RacksDB.load(schema=schema_path(), db=db_path())
    if parameters is None:
        parameters = DrawingParameters.load(DBDictsLoader({}), drawing_schema_path())
    buf = io.BytesIO()
    GltfInfrastructureDrawer(db, name, buf, parameters).draw()
    return json.loads(buf.getvalue()), db


def _nodes_by_name(document):
    return {node["name"]: node for node in document["nodes"] if "name" in node}


def _mesh_child(document, parent_name):
    by_name = _nodes_by_name(document)
    parent = by_name[parent_name]
    mesh_index = parent["children"][0]
    return document["nodes"][mesh_index]


def _equipment_mesh_children(document, equipment_name):
    by_name = _nodes_by_name(document)
    fill_node = None
    border_node = None
    for child_idx in by_name[equipment_name]["children"]:
        child = document["nodes"][child_idx]
        if child.get("extras", {}).get("category") == "equipment-border":
            border_node = child
        elif "mesh" in child:
            fill_node = child
    return fill_node, border_node


def _mesh_material(document, mesh_node):
    mesh = document["meshes"][mesh_node["mesh"]]
    material_index = mesh["primitives"][0]["material"]
    return document["materials"][material_index]


def _mesh_base_color_factor(document, mesh_node):
    return _mesh_material(document, mesh_node)["pbrMetallicRoughness"][
        "baseColorFactor"
    ]


def _ghost_base_color(colorset):
    color = list(colorset.ghost)
    color[3] = GHOST_EQUIPMENT_ALPHA
    return color


def _room_floor_slab_scale(document, room_node):
    for child_idx in room_node["children"]:
        child = document["nodes"][child_idx]
        extras = child.get("extras", {})
        if extras.get("category") == "floor" and extras.get("part") == "slab":
            return child["scale"]
    return None


def _rack_named(db, name):
    for rack in db.racks:
        if rack.name == name:
            return rack
    raise KeyError(name)


def _infrastructure_rack_names(db, infrastructure_name, parameters):
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = Path(tmpdir) / "output.png"
        drawer = InfrastructureDrawer(
            db,
            infrastructure_name,
            filename,
            "png",
            parameters,
            None,
            "json",
        )
        drawer.draw()
        return {rack.name for rack in drawer.racks}


class TestRackSlotOffset(unittest.TestCase):
    def setUp(self):
        try:
            self.schema_path = schema_path()
            self.db_path = db_path()
        except FileNotFoundError as err:
            self.skipTest(err)
        self.db = RacksDB.load(schema=self.schema_path, db=self.db_path)

    def test_empty_slot_matches_room_drawer(self):
        rack = _rack_named(self.db, "R3-A07")
        parameters = DrawingParameters.load(DBDictsLoader({}), drawing_schema_path())
        room_drawer = RoomDrawer(
            self.db,
            "noisy",
            io.BytesIO(),
            "png",
            parameters,
            None,
            "json",
        )
        room_drawer.ratio = 1
        tl = room_drawer._rack_tl(rack)
        offset = rack_slot_offset_x(self.db, rack, 1.0)
        self.assertEqual(tl.x, offset)
        # Row R3: slots 2-5 and 9-10 filled; slots 0,1,7,8 empty before A07 at slot 10.
        self.assertEqual(offset, 9 * rack.type.width)


class TestGltfInfrastructureDrawer(unittest.TestCase):
    def setUp(self):
        try:
            self.document, self.db = _load_gltf("mercury")
        except FileNotFoundError as err:
            self.skipTest(err)

    def test_asset_and_buffer(self):
        self.assertEqual(self.document["asset"]["version"], "2.0")
        self.assertEqual(len(self.document["buffers"]), 1)
        self.assertTrue(
            self.document["buffers"][0]["uri"].startswith(
                "data:application/octet-stream;base64,"
            )
        )

    def test_single_cube_accessors(self):
        accessors = self.document["accessors"]
        position = accessors[0]
        self.assertEqual(position["count"], 24)
        self.assertEqual(position["min"], [-0.5, -0.5, -0.5])
        for mesh in self.document["meshes"]:
            for prim in mesh["primitives"]:
                if prim.get("mode") == 1:
                    self.assertEqual(prim["attributes"]["POSITION"], 4)
                    self.assertEqual(prim["indices"], 5)
                    continue
                self.assertEqual(prim["attributes"]["POSITION"], 0)
                self.assertEqual(prim["attributes"]["NORMAL"], 1)
                self.assertEqual(prim["attributes"]["TEXCOORD_0"], 2)
                self.assertIn(prim["indices"], (3, 6, 7))

    def test_mesh_child_scale_on_named_nodes(self):
        by_name = _nodes_by_name(self.document)
        for name in ("R1-A01", "mecn0001"):
            parent = by_name[name]
            self.assertNotIn("scale", parent)
        child = _mesh_child(self.document, "mecn0001")
        self.assertEqual(child["scale"], by_name["mecn0001"]["extras"]["size"])

    def test_mecn0001_expanded_and_centered(self):
        by_name = _nodes_by_name(self.document)
        self.assertIn("mecn0001", by_name)
        self.assertNotIn("mecn[0001-0040]", by_name)
        node = by_name["mecn0001"]
        rack = _rack_named(self.db, "R1-A01")
        pane = 40
        interior = rack.type.width - 2 * pane
        eq_w = 0.5 * interior
        cx = (pane + eq_w / 2 - rack.type.width / 2) * 0.001
        cy = (0 + 1 * 44.45 / 2 - rack.type.height / 2) * 0.001
        cz = EQUIPMENT_BACK_INSET_M / 2
        for actual, expected in zip(node["translation"], [cx, cy, cz]):
            self.assertAlmostEqual(actual, expected, places=5)
        self.assertAlmostEqual(node["extras"]["size"][0], eq_w * 0.001)
        self.assertAlmostEqual(node["extras"]["size"][1], 1 * 44.45 * 0.001)
        self.assertAlmostEqual(
            node["extras"]["size"][2],
            rack.type.depth * 0.001 - EQUIPMENT_BACK_INSET_M,
        )
        borders = [
            self.document["nodes"][child_idx]
            for child_idx in node["children"]
            if self.document["nodes"][child_idx].get("extras", {}).get("category")
            == "equipment-border"
        ]
        self.assertEqual(len(borders), 1)
        self.assertEqual(borders[0]["scale"], node["extras"]["size"])
        border_mesh = self.document["meshes"][borders[0]["mesh"]]
        self.assertEqual(border_mesh["primitives"][0]["mode"], 1)

    def test_rack_carcass_panels_and_floor_texture(self):
        by_name = _nodes_by_name(self.document)
        rack = by_name["R1-A01"]
        parts = {}
        for child_idx in rack["children"]:
            child = self.document["nodes"][child_idx]
            extras = child.get("extras", {})
            if extras.get("category") == "rack-part":
                parts[extras["part"]] = child
        self.assertEqual(set(parts), {"left", "right", "top", "bottom"})
        self.assertNotIn("front", parts)
        pane = 0.04 - EQUIPMENT_SIDE_CLEARANCE_M
        rack_width = rack["extras"]["size"][0]
        self.assertAlmostEqual(parts["left"]["scale"][0], pane)
        self.assertAlmostEqual(parts["right"]["scale"][0], pane)
        self.assertAlmostEqual(
            parts["left"]["translation"][0] - parts["left"]["scale"][0] / 2,
            -rack_width / 2,
        )
        self.assertAlmostEqual(
            parts["right"]["translation"][0] + parts["right"]["scale"][0] / 2,
            rack_width / 2,
        )
        self.assertIn("KHR_texture_transform", self.document["extensionsUsed"])
        sampler = self.document["samplers"][0]
        self.assertEqual(sampler["magFilter"], 9729)
        self.assertEqual(sampler["minFilter"], 9987)
        self.assertEqual(sampler["wrapS"], 10497)
        self.assertEqual(sampler["wrapT"], 10497)
        prefix = "data:image/png;base64,"
        for index, path in (
            (0, FLOOR_TILE_SOLID_PNG),
            (1, FLOOR_TILE_PERFORATED_PNG),
        ):
            image = self.document["images"][index]["uri"]
            self.assertTrue(image.startswith(prefix))
            self.assertEqual(
                base64.b64decode(image[len(prefix) :]),
                path.read_bytes(),
            )
        floors = [
            node
            for node in self.document["nodes"]
            if node.get("extras", {}).get("category") == "floor"
        ]
        slabs = [f for f in floors if f.get("extras", {}).get("part") == "slab"]
        vents = [f for f in floors if f.get("extras", {}).get("part") == "perforated"]
        self.assertEqual(len(slabs), 1)
        self.assertGreaterEqual(len(vents), 1)
        floor_mesh = self.document["meshes"][slabs[0]["mesh"]]
        top_primitive = next(
            prim for prim in floor_mesh["primitives"] if prim["indices"] == 6
        )
        material = self.document["materials"][top_primitive["material"]]
        texture = material["pbrMetallicRoughness"]["baseColorTexture"]
        scale = texture["extensions"]["KHR_texture_transform"]["scale"]
        room = by_name["noisy"]
        self.assertAlmostEqual(scale[0], room["extras"]["size"][0] / FLOOR_TILE_M)
        self.assertAlmostEqual(scale[1], room["extras"]["size"][2] / FLOOR_TILE_M)
        vent_mesh = self.document["meshes"][vents[0]["mesh"]]
        vent_material = self.document["materials"][
            vent_mesh["primitives"][0]["material"]
        ]
        vent_texture = vent_material["pbrMetallicRoughness"]["baseColorTexture"]
        self.assertEqual(vent_texture["index"], 1)
        vent_scale = vent_texture["extensions"]["KHR_texture_transform"]["scale"]
        self.assertEqual(vent_scale, [1.0, 1.0])

    def test_perforated_floor_in_front_of_rack_doors(self):
        vents = [
            node
            for node in self.document["nodes"]
            if node.get("extras", {}).get("part") == "perforated"
        ]
        translations = {tuple(node["translation"]) for node in vents}

        r1_row_z = 4.0
        r1_center_z = r1_row_z + 0.457
        r1_door_strip_z = (4.914, 5.514)
        r1_a01_vent = (3.3, 5.7)
        self.assertIn(
            (r1_a01_vent[0], vents[0]["translation"][1], r1_a01_vent[1]),
            translations,
        )
        neighbor_odd = (3.3, 5.1)
        self.assertNotIn(
            (neighbor_odd[0], vents[0]["translation"][1], neighbor_odd[1]),
            translations,
        )
        self.assertGreater(r1_a01_vent[1], r1_center_z)
        self.assertGreaterEqual(r1_a01_vent[1], r1_door_strip_z[0])
        self.assertLessEqual(r1_a01_vent[1], r1_door_strip_z[1] + FLOOR_TILE_M)

        r2_row_z = 6.0
        r2_center_z = r2_row_z + 0.457
        r2_vent_z = {t[2] for t in translations if abs(t[0] - 4.5) < 0.01}
        self.assertEqual(len(r2_vent_z), 1)
        self.assertLess(next(iter(r2_vent_z)), r2_center_z)

    def test_rack_door_orientation(self):
        by_name = _nodes_by_name(self.document)
        self.assertNotIn("rotation", by_name["R1-A01"])
        self.assertEqual(by_name["R2-A02"]["rotation"], [0.0, 1.0, 0.0, 0.0])
        mesh = _mesh_child(self.document, "R1-A01")
        self.assertNotIn("rotation", mesh)

    def test_r1_a02_slot_offset(self):
        by_name = _nodes_by_name(self.document)
        rack = _rack_named(self.db, "R1-A02")
        offset_mm = rack_slot_offset_x(self.db, rack, 1.0)
        expected_x = (offset_mm + rack.type.width / 2) * 0.001
        self.assertAlmostEqual(by_name["R1-A02"]["translation"][0], expected_x)
        self.assertAlmostEqual(expected_x, 0.9)

    def test_equipment_tags_ghost(self):
        params = DrawingParameters.load(
            DBDictsLoader(
                {
                    "infrastructure": {
                        "equipment_tags": ["gpu"],
                        "ghost_unselected": True,
                    }
                }
            ),
            drawing_schema_path(),
        )
        document, db = _load_gltf("mercury", params)
        by_name = _nodes_by_name(document)
        self.assertIn("megpu0001", by_name)
        self.assertTrue(by_name["megpu0001"]["extras"]["selected"])
        self.assertIn("mesrv0001", by_name)
        self.assertFalse(by_name["mesrv0001"]["extras"]["selected"])

        ghost_equipment = db.infrastructures["mercury"].nodes["mesrv0001"]
        ghost_colorset = find_equipment_colorset(params, ghost_equipment)
        expected = _ghost_base_color(ghost_colorset)
        ghost_fill, ghost_border = _equipment_mesh_children(document, "mesrv0001")
        self.assertEqual(_mesh_base_color_factor(document, ghost_fill), expected)
        self.assertEqual(_mesh_base_color_factor(document, ghost_border), expected)
        fill_material = _mesh_material(document, ghost_fill)
        border_material = _mesh_material(document, ghost_border)
        for material in document["materials"]:
            if material is fill_material or material is border_material:
                self.assertEqual(material["alphaMode"], "BLEND")
            else:
                self.assertNotEqual(material.get("alphaMode"), "BLEND")

        params_no_ghost = DrawingParameters.load(
            DBDictsLoader({"infrastructure": {"equipment_tags": ["gpu"]}}),
            drawing_schema_path(),
        )
        document2, _ = _load_gltf("mercury", params_no_ghost)
        by_name2 = _nodes_by_name(document2)
        self.assertIn("megpu0001", by_name2)
        self.assertNotIn("mesrv0001", by_name2)

    def test_other_racks_and_discard_match_elevation(self):
        for other_racks, discard_empty in ((True, False), (False, True)):
            overrides = {
                "infrastructure": {
                    "other_racks": other_racks,
                    "discard_empty_racks": discard_empty,
                }
            }
            params = DrawingParameters.load(
                DBDictsLoader(overrides), drawing_schema_path()
            )
            document, db = _load_gltf("mercury", params)
            gltf_racks = {
                n["name"]
                for n in document["nodes"]
                if n.get("extras", {}).get("category") == "rack"
            }
            png_racks = _infrastructure_rack_names(db, "mercury", params)
            self.assertEqual(gltf_racks, png_racks)

    def test_other_racks_carcass_without_equipment(self):
        params = DrawingParameters.load(
            DBDictsLoader({"infrastructure": {"other_racks": True}}),
            drawing_schema_path(),
        )
        document, _ = _load_gltf("mercury", params)
        by_name = _nodes_by_name(document)
        # R1-A03 is in the same row but not in mercury layout
        if "R1-A03" in by_name:
            rack = by_name["R1-A03"]
            self.assertFalse(rack["extras"]["in_infrastructure"])
            parts = []
            for child_idx in rack["children"]:
                child = document["nodes"][child_idx]
                part = child.get("extras", {}).get("part")
                if child.get("extras", {}).get("category") == "rack-part":
                    parts.append(part)
                    continue
                if "name" in child:
                    self.fail("other_racks carcass must not have equipment children")
            self.assertIn("front", parts)

    def test_jupiter_multi_room(self):
        document, _ = _load_gltf("jupiter")
        rooms = {
            n["name"]: n
            for n in document["nodes"]
            if n.get("extras", {}).get("category") == "room"
        }
        self.assertIn("level2", rooms)
        self.assertIn("noisy", rooms)
        self.assertEqual(rooms["level2"]["extras"]["datacenter"], "london")
        self.assertEqual(rooms["noisy"]["extras"]["datacenter"], "paris")
        level2 = rooms["level2"]
        noisy = rooms["noisy"]
        level2_width = level2["extras"]["size"][0]
        self.assertAlmostEqual(level2["translation"][0], 0.0)
        self.assertAlmostEqual(noisy["translation"][0], level2_width + ROOM_GAP_M)
        level2_slab = _room_floor_slab_scale(document, level2)
        noisy_slab = _room_floor_slab_scale(document, noisy)
        self.assertIsNotNone(level2_slab)
        self.assertIsNotNone(noisy_slab)
        self.assertAlmostEqual(level2_slab[0], level2_width)
        self.assertAlmostEqual(level2_slab[2], level2["extras"]["size"][2])
        self.assertAlmostEqual(noisy_slab[0], noisy["extras"]["size"][0])
        self.assertAlmostEqual(noisy_slab[2], noisy["extras"]["size"][2])

    def test_jupiter_row_rotation(self):
        document, _ = _load_gltf("jupiter")
        by_name = _nodes_by_name(document)
        row = by_name["R5"]
        angle = -math.radians(row["extras"]["rotation"])
        half = angle / 2
        expected = [0.0, math.sin(half), 0.0, math.cos(half)]
        for a, b in zip(row["rotation"], expected):
            self.assertAlmostEqual(a, b, places=5)

    def test_extras_keys(self):
        by_name = _nodes_by_name(self.document)
        rack_keys = {
            "category",
            "type",
            "in_infrastructure",
            "reversed",
            "slots",
            "size",
        }
        self.assertEqual(set(by_name["R1-A01"]["extras"].keys()), rack_keys)
        equip_keys = {
            "category",
            "type",
            "tags",
            "selected",
            "size",
            "rack",
            "slot",
        }
        self.assertEqual(set(by_name["mecn0001"]["extras"].keys()), equip_keys)

    def test_equipment_colors_match_drawing_parameters(self):
        parameters = DrawingParameters.load(DBDictsLoader({}), drawing_schema_path())
        by_name = _nodes_by_name(self.document)
        equipment = self.db.infrastructures["mercury"].nodes["mecn0001"]
        colorset = find_equipment_colorset(parameters, equipment)
        fill_node, border_node = _equipment_mesh_children(self.document, "mecn0001")
        self.assertIsNotNone(fill_node)
        self.assertIsNotNone(border_node)
        self.assertEqual(
            _mesh_base_color_factor(self.document, fill_node),
            list(colorset.background),
        )
        self.assertEqual(
            _mesh_base_color_factor(self.document, border_node),
            list(colorset.border),
        )

        params = DrawingParameters.load(
            DBDictsLoader(
                {
                    "infrastructure": {
                        "equipment_tags": ["gpu"],
                        "ghost_unselected": True,
                    }
                }
            ),
            drawing_schema_path(),
        )
        document, db = _load_gltf("mercury", params)
        ghost_equipment = db.infrastructures["mercury"].nodes["mesrv0001"]
        ghost_colorset = find_equipment_colorset(params, ghost_equipment)
        ghost_extras = _nodes_by_name(document)["mesrv0001"]["extras"]
        self.assertFalse(ghost_extras["selected"])
        ghost_fill, ghost_border = _equipment_mesh_children(document, "mesrv0001")
        ghost_color = _ghost_base_color(ghost_colorset)
        self.assertEqual(_mesh_base_color_factor(document, ghost_fill), ghost_color)
        self.assertEqual(_mesh_base_color_factor(document, ghost_border), ghost_color)
