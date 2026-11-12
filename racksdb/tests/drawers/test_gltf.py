# Copyright (c) 2026 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import base64
from itertools import chain
import io
import json
import struct
import unittest

from racksdb import RacksDB
from racksdb.drawers import (
    drawer_class,
    AxonometricInfrastructureDrawer,
    GltfInfrastructureDrawer,
    InfrastructureDrawer,
    RoomDrawer,
)
from racksdb.drawers.gltf import ASSETS_DIR, _linear, GLB_MAGIC
from racksdb.drawers.parameters import DrawingParameters
from racksdb.drawers.room import RoomDrawer as _RoomDrawer
from racksdb.generic.db import DBDictsLoader
from racksdb.errors import RacksDBDrawingError

from ..lib.common import drawing_schema_path, schema_path, db_path


def parse_glb(content: bytes):
    """Return the tuple (document, binary chunk) of GLB content."""
    magic, version, length = struct.unpack_from("<III", content, 0)
    assert magic == GLB_MAGIC and version == 2 and length == len(content)
    json_length, json_type = struct.unpack_from("<II", content, 12)
    assert json_type == 0x4E4F534A
    document = json.loads(content[20 : 20 + json_length])
    offset = 20 + json_length
    bin_length, bin_type = struct.unpack_from("<II", content, offset)
    assert bin_type == 0x004E4942
    return document, content[offset + 8 : offset + 8 + bin_length]


def _quat_rotate(q, v):
    """Rotate vector v by unit quaternion q (x, y, z, w)."""
    x, y, z, w = q
    # t = 2 * cross(q.xyz, v)
    tx = 2 * (y * v[2] - z * v[1])
    ty = 2 * (z * v[0] - x * v[2])
    tz = 2 * (x * v[1] - y * v[0])
    # v + w * t + cross(q.xyz, t)
    return (
        v[0] + w * tx + (y * tz - z * ty),
        v[1] + w * ty + (z * tx - x * tz),
        v[2] + w * tz + (x * ty - y * tx),
    )


def world_positions(document):
    """Return dict of world positions of the origins of all named nodes. Named nodes
    are never scaled, so only translations and rotations are considered."""
    nodes = document["nodes"]
    result = {}

    def visit(index, transforms):
        node = nodes[index]
        transforms = [
            (node.get("translation", [0, 0, 0]), node.get("rotation", [0, 0, 0, 1]))
        ] + transforms
        if "name" in node:
            point = (0.0, 0.0, 0.0)
            for translation, rotation in transforms:
                point = _quat_rotate(rotation, point)
                point = tuple(p + t for p, t in zip(point, translation))
            result[node["name"]] = point
        for child in node.get("children", []):
            visit(child, transforms)

    for root in document["scenes"][0]["nodes"]:
        visit(root, [])
    return result


class TestGltfInfrastructureDrawer(unittest.TestCase):
    def setUp(self):
        try:
            self.drawings_schema_path = drawing_schema_path()
            self.schema_path = schema_path()
            self.db_path = db_path()
        except FileNotFoundError as err:
            self.skipTest(err)
        self.db = RacksDB.load(schema=self.schema_path, db=self.db_path)

    def parameters(self, content=None):
        return DrawingParameters.load(
            DBDictsLoader(content or {}), self.drawings_schema_path
        )

    def draw(self, name="mercury", output_format="glb", parameters=None):
        """Draw infrastructure and return the tuple (raw content, glTF document,
        binary buffer)."""
        file = io.BytesIO()
        GltfInfrastructureDrawer(
            self.db,
            name,
            file,
            output_format,
            parameters or self.parameters(),
        ).draw()
        content = file.getvalue()
        if output_format == "glb":
            document, blob = parse_glb(content)
        else:
            document = json.loads(content)
            uri = document["buffers"][0]["uri"]
            prefix = "data:application/octet-stream;base64,"
            self.assertTrue(uri.startswith(prefix))
            blob = base64.b64decode(uri[len(prefix) :])
        return content, document, blob

    def nodes(self, document, **extras):
        """Return list of nodes with matching extras."""
        return [
            node
            for node in document["nodes"]
            if all(node.get("extras", {}).get(k) == v for k, v in extras.items())
        ]

    def node(self, document, name):
        (node,) = [node for node in document["nodes"] if node.get("name") == name]
        return node

    def children(self, document, node):
        return [document["nodes"][index] for index in node.get("children", [])]

    def parts(self, document, node, part=None):
        """Return geometry children nodes, with the given part if not None."""
        return [
            child
            for child in self.children(document, node)
            if "part" in child.get("extras", {})
            and (part is None or child["extras"]["part"] == part)
        ]

    #
    # Formats
    #

    def test_glb_and_gltf_equivalent(self):
        _, glb_document, glb_blob = self.draw(output_format="glb")
        _, gltf_document, gltf_blob = self.draw(output_format="gltf")
        # GLB binary chunk is padded to 4 bytes boundary.
        self.assertEqual(len(glb_blob) % 4, 0)
        self.assertEqual(glb_blob[: len(gltf_blob)], gltf_blob)
        self.assertEqual(glb_document["buffers"][0]["byteLength"], len(gltf_blob))
        del gltf_document["buffers"][0]["uri"]
        self.assertEqual(glb_document, gltf_document)

    def test_glb_alignment(self):
        content, document, _ = self.draw()
        json_length = struct.unpack_from("<I", content, 12)[0]
        self.assertEqual(json_length % 4, 0)
        for buffer_view in document["bufferViews"]:
            self.assertEqual(buffer_view["byteOffset"] % 4, 0)

    def test_asset(self):
        _, document, _ = self.draw()
        self.assertEqual(document["asset"]["version"], "2.0")
        self.assertEqual(document["extensionsUsed"], ["KHR_texture_transform"])
        self.assertNotIn("extensionsRequired", document)

    def test_accessors_bounds(self):
        _, document, blob = self.draw()
        for accessor in document["accessors"]:
            view = document["bufferViews"][accessor["bufferView"]]
            component_size = 4 if accessor["componentType"] == 5126 else 2
            components = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}[accessor["type"]]
            self.assertEqual(
                view["byteLength"], accessor["count"] * components * component_size
            )
            self.assertLessEqual(view["byteOffset"] + view["byteLength"], len(blob))

    def test_images_in_buffer(self):
        _, document, blob = self.draw()
        self.assertEqual(len(document["images"]), 2)
        for image, name in zip(
            document["images"], ["floor-tile-solid.png", "floor-tile-perforated.png"]
        ):
            self.assertEqual(image["mimeType"], "image/png")
            self.assertNotIn("uri", image)
            view = document["bufferViews"][image["bufferView"]]
            self.assertEqual(
                blob[view["byteOffset"] : view["byteOffset"] + view["byteLength"]],
                (ASSETS_DIR / name).read_bytes(),
            )

    def test_output_size(self):
        # Guard against heavy textures or geometry duplication.
        for asset in ASSETS_DIR.glob("*.png"):
            self.assertLess(asset.stat().st_size, 64 * 1024)
        content, _, _ = self.draw()
        self.assertLess(len(content), 150 * 1024)

    def test_write_file(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "mercury.glb"
            GltfInfrastructureDrawer(
                self.db, "mercury", filename, "glb", self.parameters()
            ).draw()
            parse_glb(filename.read_bytes())

    #
    # Errors
    #

    def test_not_existing_infrastructure(self):
        with self.assertRaisesRegex(
            RacksDBDrawingError, "^Unable to find infrastructure fail in database$"
        ):
            GltfInfrastructureDrawer(
                self.db, "fail", io.BytesIO(), "glb", self.parameters()
            )

    def test_unsupported_format(self):
        with self.assertRaisesRegex(RacksDBDrawingError, "^Unsupported 3D format png$"):
            GltfInfrastructureDrawer(
                self.db, "mercury", io.BytesIO(), "png", self.parameters()
            )

    def test_coordinates(self):
        with self.assertRaisesRegex(
            RacksDBDrawingError, "^Coordinates are not supported with glb format$"
        ):
            GltfInfrastructureDrawer(
                self.db,
                "mercury",
                io.BytesIO(),
                "glb",
                self.parameters(),
                io.StringIO(),
                "json",
            )

    def test_no_racks(self):
        with self.assertRaisesRegex(
            RacksDBDrawingError, "^Unable to find racks to draw with filters"
        ):
            self.draw(
                parameters=self.parameters(
                    {"infrastructure": {"equipment_tags": ["fail"]}}
                )
            )

    #
    # Scene graph
    #

    def test_hierarchy(self):
        _, document, _ = self.draw()
        roots = [document["nodes"][index] for index in document["scenes"][0]["nodes"]]
        self.assertEqual([root["name"] for root in roots], ["noisy"])
        self.assertEqual(roots[0]["extras"]["category"], "room")
        self.assertEqual(roots[0]["extras"]["datacenter"], "paris")
        rows = [child for child in self.children(document, roots[0]) if "name" in child]
        self.assertEqual([row["name"] for row in rows], ["R1", "R2"])
        self.assertEqual(rows[1]["extras"], {"category": "row", "reversed": True})
        racks = [
            child["name"]
            for row in rows
            for child in self.children(document, row)
            if "name" in child
        ]
        self.assertEqual(racks, ["R1-A01", "R1-A02", "R2-A02", "R2-A03"])
        # All equipment of infrastructure parts are represented in their racks.
        infrastructure = self.db.infrastructures["mercury"]
        for part in infrastructure.layout:
            rack = self.node(document, part.rack.name)
            self.assertCountEqual(
                [c["name"] for c in self.children(document, rack) if "name" in c],
                [
                    equipment.name
                    for equipment in chain(
                        part.nodes, part.storage, part.network, part.misc
                    )
                ],
            )

    def test_named_nodes_not_scaled(self):
        _, document, _ = self.draw()
        for node in document["nodes"]:
            if "name" in node:
                self.assertNotIn("scale", node)
                self.assertNotIn("mesh", node)
            else:
                self.assertIn("mesh", node)
                self.assertIn("part", node["extras"])

    def test_rack_extras(self):
        _, document, _ = self.draw()
        rack = self.node(document, "R1-A01")
        self.assertEqual(
            rack["extras"],
            {
                "category": "rack",
                "type": "standard",
                "tags": ["first"],
                "infrastructure": True,
                "size": [0.6, 1.867, 0.914],
            },
        )
        self.assertNotIn("rotation", rack)
        # Racks of reversed rows are rotated by 180°.
        self.assertEqual(self.node(document, "R2-A02")["rotation"], [0, 1, 0, 0])
        parts = [c["extras"]["part"] for c in self.parts(document, rack)]
        self.assertEqual(parts[:4], ["left", "right", "top", "bottom"])
        self.assertNotIn("door", parts)

    def test_equipment(self):
        _, document, _ = self.draw()
        equipment = self.node(document, "mecn0001")
        self.assertEqual(
            equipment["extras"],
            {
                "category": "node",
                "type": "sm220bt",
                "tags": ["compute"],
                "rack": "R1-A01",
                "slot": {"height": 0, "width": 0},
                "selected": True,
                "colliding": False,
                "size": [0.26, 0.04445, 0.814],
            },
        )
        # Half width node on the left side, in the lowest slot, with its front face
        # aligned on rack door.
        self.assertEqual(
            equipment["translation"],
            [round(0.04 + 0.13 - 0.3, 6), round(0.022225 - 1.867 / 2, 6), 0.05],
        )
        self.assertEqual(
            [c["extras"]["part"] for c in self.children(document, equipment)],
            ["body", "edges"],
        )
        for category in ["storage", "network", "misc"]:
            self.assertTrue(self.nodes(document, category=category))

    def test_racks_positions_match_room_maps(self):
        """Racks centers in 3D scene match racks footprints in rooms maps, including
        rows rotations, reversed rows and multiple rooms."""
        for name in ["mercury", "jupiter", "sharednet"]:
            _, document, _ = self.draw(name)
            positions = world_positions(document)
            room_offsets = {
                document["nodes"][index]["name"]: document["nodes"][index][
                    "translation"
                ][0]
                for index in document["scenes"][0]["nodes"]
            }
            racks = self.nodes(document, category="rack")
            self.assertTrue(racks)
            for rack_node in racks:
                (rack,) = [r for r in self.db.racks if r.name == rack_node["name"]]
                room_drawer = _RoomDrawer(
                    self.db, rack.room.name, None, "png", self.parameters(), None, None
                )
                footprint = room_drawer._rack_footprint(rack)
                center_x = sum(point[0] for point in footprint) / 4 / 1000
                center_z = sum(point[1] for point in footprint) / 4 / 1000
                x, y, z = positions[rack.name]
                # Nodes coordinates are rounded to micrometers.
                self.assertAlmostEqual(
                    x, room_offsets[rack.room.name] + center_x, places=5
                )
                self.assertAlmostEqual(y, rack.type.height / 2 / 1000, places=5)
                self.assertAlmostEqual(z, center_z, places=5)

    def test_racks_footprints_match_room_drawer(self):
        """Racks footprints, including racks after empty slots, match room drawer."""
        drawer = GltfInfrastructureDrawer(
            self.db, "mercury", io.BytesIO(), "glb", self.parameters()
        )
        for datacenter in self.db.datacenters:
            for room in datacenter.rooms:
                room_drawer = _RoomDrawer(
                    self.db, room.name, None, "png", self.parameters(), None, None
                )
                for row in room.rows:
                    for rack in row.racks:
                        self.assertEqual(
                            drawer._rack_footprint(rack),
                            room_drawer._rack_footprint(rack),
                        )

    def test_multiple_rooms(self):
        _, document, _ = self.draw("jupiter")
        roots = [document["nodes"][index] for index in document["scenes"][0]["nodes"]]
        self.assertEqual([root["name"] for root in roots], ["level2", "noisy"])
        self.assertEqual(roots[0]["translation"], [0, 0, 0])
        # Rooms are placed side by side with a gap of 2 meters.
        level2 = self.db.datacenters["london"].rooms["level2"]
        self.assertEqual(
            roots[1]["translation"], [level2.dimensions.width / 1000 + 2, 0, 0]
        )
        self.assertEqual(roots[1]["extras"]["datacenter"], "paris")

    def test_row_rotation(self):
        _, document, _ = self.draw("jupiter")
        # Row E is rotated by 90° clockwise when viewed from above.
        row = self.node(document, "E")
        self.assertEqual(row["rotation"], [0, -0.707107, 0, 0.707107])

    #
    # Floor
    #

    def test_floor(self):
        _, document, _ = self.draw()
        room = self.node(document, "noisy")
        (floor,) = self.parts(document, room, "floor")
        self.assertEqual(floor["scale"], [14, 0.3, 25])
        self.assertEqual(floor["translation"], [7, -0.152, 12.5])
        mesh = document["meshes"][floor["mesh"]]
        top = document["materials"][mesh["primitives"][0]["material"]]
        transform = top["pbrMetallicRoughness"]["baseColorTexture"]["extensions"][
            "KHR_texture_transform"
        ]
        # One texture repetition per 600mm tile
        self.assertEqual(transform["scale"], [round(14 / 0.6, 6), round(25 / 0.6, 6)])
        # Base color factors must be in [0, 1] range.
        for material in document["materials"]:
            for value in material["pbrMetallicRoughness"]["baseColorFactor"]:
                self.assertTrue(0 <= value <= 1)

    def test_perforated_tiles(self):
        _, document, _ = self.draw()
        tiles = sorted(
            (
                round(tile["translation"][0] / 0.6 - 0.5),
                round(tile["translation"][2] / 0.6 - 0.5),
            )
            for tile in self.nodes(document, part="perforated-tile")
        )
        # Rows R1 (doors on bottom) and R2 (reversed, doors on top) face each other
        # with 1086mm between them, perforated tiles are in this cold aisle in a
        # checkerboard pattern.
        self.assertEqual(tiles, [(5, 9), (6, 8), (7, 9)])

    def test_perforated_tiles_not_under_racks(self):
        for name in ["mercury", "jupiter", "sharednet"]:
            drawer = GltfInfrastructureDrawer(
                self.db, name, io.BytesIO(), "glb", self.parameters()
            )
            drawer.draw()
            for room in drawer._rooms():
                room_racks = drawer._room_racks(room)
                tiles = drawer._perforated_tiles(room, room_racks)
                self.assertTrue(tiles)
                for ix, iz in tiles:
                    self.assertEqual((ix + iz) % 2, 0)
                    self.assertTrue(0 <= ix < room.dimensions.width / 600)
                    self.assertTrue(0 <= iz < room.dimensions.depth / 600)

    #
    # Drawing parameters
    #

    def test_equipment_tags(self):
        _, document, _ = self.draw(
            parameters=self.parameters(
                {"infrastructure": {"equipment_tags": ["compute"]}}
            )
        )
        # Racks with only unselected equipment are discarded by default.
        self.assertEqual(
            [rack["name"] for rack in self.nodes(document, category="rack")],
            ["R1-A01", "R1-A02"],
        )
        self.assertFalse(self.nodes(document, selected=False))

    def test_ghost_unselected(self):
        _, document, _ = self.draw(
            parameters=self.parameters(
                {
                    "infrastructure": {
                        "equipment_tags": ["compute"],
                        "ghost_unselected": True,
                        "discard_empty_racks": False,
                    }
                }
            )
        )
        self.assertEqual(len(self.nodes(document, category="rack")), 4)
        ghost = self.node(document, "mesrv0001")
        self.assertFalse(ghost["extras"]["selected"])
        body = self.children(document, ghost)[0]
        mesh = document["meshes"][body["mesh"]]
        material = document["materials"][mesh["primitives"][0]["material"]]
        self.assertEqual(material["alphaMode"], "BLEND")
        self.assertEqual(material["pbrMetallicRoughness"]["baseColorFactor"][3], 0.4)

    def test_other_racks(self):
        _, document, _ = self.draw(
            parameters=self.parameters({"infrastructure": {"other_racks": True}})
        )
        rack = self.node(document, "R1-A03")
        self.assertFalse(rack["extras"]["infrastructure"])
        children = self.children(document, rack)
        self.assertIn("door", [c["extras"]["part"] for c in children])
        self.assertFalse([c for c in children if "name" in c])

    def test_equipment_colors(self):
        _, document, _ = self.draw(
            parameters=self.parameters(
                {
                    "colors": {
                        "equipments": [
                            {"type": "sm220bt", "background": "#FF0000"},
                        ],
                        "racks": [{"frame": "#00FF00"}],
                    }
                }
            )
        )

        def material(node, part):
            (child,) = self.parts(document, node, part)
            mesh = document["meshes"][child["mesh"]]
            return document["materials"][mesh["primitives"][0]["material"]][
                "pbrMetallicRoughness"
            ]["baseColorFactor"]

        self.assertEqual(
            material(self.node(document, "mecn0001"), "body"), [1, 0, 0, 1]
        )
        # Default background color #999999 converted to linear RGB
        self.assertEqual(
            material(self.node(document, "mesrv0001"), "body"),
            [0.318547, 0.318547, 0.318547, 1],
        )
        self.assertEqual(material(self.node(document, "R1-A01"), "left"), [0, 1, 0, 1])

    def test_collisions(self):
        def edges_color(document, name):
            (edges,) = self.parts(document, self.node(document, name), "edges")
            mesh = document["meshes"][edges["mesh"]]
            self.assertEqual(mesh["primitives"][0]["mode"], 1)
            return document["materials"][mesh["primitives"][0]["material"]][
                "pbrMetallicRoughness"
            ]["baseColorFactor"]

        with self.assertLogs("racksdb.drawers.collisions", level="WARNING"):
            _, document, _ = self.draw()
        self.assertTrue(self.node(document, "swnas01")["extras"]["colliding"])
        self.assertEqual(edges_color(document, "swnas01"), [1, 0, 0, 1])
        self.assertNotEqual(edges_color(document, "mesw01"), [1, 0, 0, 1])

        with self.assertLogs("racksdb.drawers.collisions", level="WARNING"):
            _, document, _ = self.draw(
                parameters=self.parameters({"infrastructure": {"collisions": False}})
            )
        self.assertTrue(self.node(document, "swnas01")["extras"]["colliding"])
        self.assertNotEqual(edges_color(document, "swnas01"), [1, 0, 0, 1])


class TestGltfHelpers(unittest.TestCase):
    def test_linear(self):
        self.assertEqual(_linear((0, 0, 0, 1)), (0, 0, 0, 1))
        self.assertEqual(_linear((1, 1, 1, 0.5)), (1, 1, 1, 0.5))
        self.assertEqual(_linear((0.6, 0.6, 0.6, 1))[0], 0.318547)
        self.assertEqual(_linear((0.04, 0, 0, 1))[0], round(0.04 / 12.92, 6))


class TestDrawerClass(unittest.TestCase):
    def setUp(self):
        try:
            self.parameters = DrawingParameters.load(
                DBDictsLoader({}), drawing_schema_path()
            )
            self.axonometric = DrawingParameters.load(
                DBDictsLoader({"axonometric": {"enabled": True}}),
                drawing_schema_path(),
            )
        except FileNotFoundError as err:
            self.skipTest(err)

    def test_classes(self):
        for output_format in ["png", "svg", "pdf"]:
            self.assertIs(
                drawer_class("infrastructure", output_format, self.parameters),
                InfrastructureDrawer,
            )
            self.assertIs(
                drawer_class("infrastructure", output_format, self.axonometric),
                AxonometricInfrastructureDrawer,
            )
            self.assertIs(
                drawer_class("room", output_format, self.parameters), RoomDrawer
            )
        for output_format in ["gltf", "glb"]:
            for parameters in [self.parameters, self.axonometric]:
                self.assertIs(
                    drawer_class("infrastructure", output_format, parameters),
                    GltfInfrastructureDrawer,
                )

    def test_errors(self):
        with self.assertRaisesRegex(
            RacksDBDrawingError, "^Unable to draw entity fail$"
        ):
            drawer_class("fail", "png", self.parameters)
        with self.assertRaisesRegex(
            RacksDBDrawingError, "^Format glb is only supported for infrastructures$"
        ):
            drawer_class("room", "glb", self.parameters)
        with self.assertRaisesRegex(
            RacksDBDrawingError, "^Coordinates are not supported with gltf format$"
        ):
            drawer_class("infrastructure", "gltf", self.parameters, coordinates=True)
