# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import base64
import json
import logging
import math
import struct
from pathlib import Path

from ..errors import RacksDBDrawingError
from .base import find_equipment_colorset
from .layout import (
    equipment_matches_tags,
    infrastructure_part_for_rack,
    rack_in_infrastructure,
    rack_slot_offset_x,
    select_infrastructure_racks,
)

logger = logging.getLogger(__name__)

MM_TO_M = 0.001
FLOOR_THICKNESS_M = 0.3
# Keep the slab just below the racks so panel bottoms do not flicker on the floor.
FLOOR_CLEARANCE_M = 0.002
FLOOR_TILE_M = 0.6
FLOOR_VENT_LIFT_M = 0.0005
# Horizontal gap between room roots when an infrastructure spans multiple rooms.
ROOM_GAP_M = 2.0
# Brighten tiled albedo so the slab reads light under typical viewer lighting.
# Factor is sRGB-encoded so Three.js matches a linear RGB gain of ~1.12.
FLOOR_BASE_COLOR_FACTOR = [1.051, 1.051, 1.051, 1.0]
FLOOR_SIDE_COLOR = [0.34, 0.36, 0.40, 1.0]
FLOOR_ROUGHNESS = 0.78
_ASSETS_DIR = Path(__file__).resolve().parent / "assets"
FLOOR_TILE_SOLID_PNG = _ASSETS_DIR / "floor-tile-solid.png"
FLOOR_TILE_PERFORATED_PNG = _ASSETS_DIR / "floor-tile-perforated.png"
# Equipment is this much shorter than the rack, taken from the rear (-Z).
EQUIPMENT_BACK_INSET_M = 0.1
# Sheet thickness of the top and bottom of a rack carcass.
SHELL_THICKNESS_M = 0.008
# Step side-pane inner faces back so they are not coplanar with equipment sides.
EQUIPMENT_SIDE_CLEARANCE_M = 0.001
RACK_COLOR = [0.15, 0.15, 0.16, 1.0]
EQUIPMENT_FILL_ROUGHNESS = 1.0
EQUIPMENT_BORDER_ROUGHNESS = 0.9
# Default ghost colors are opaque hex RGB. three.js ignores baseColorFactor
# alpha unless alphaMode is BLEND, so give those chassis a visible fade.
GHOST_EQUIPMENT_ALPHA = 0.4

# Unit cube with flat normals, 24 vertices, 36 indices (12 triangles).
_CUBE_POSITIONS = (
    # +X
    (0.5, -0.5, -0.5),
    (0.5, 0.5, -0.5),
    (0.5, 0.5, 0.5),
    (0.5, -0.5, 0.5),
    # -X
    (-0.5, -0.5, 0.5),
    (-0.5, 0.5, 0.5),
    (-0.5, 0.5, -0.5),
    (-0.5, -0.5, -0.5),
    # +Y
    (-0.5, 0.5, -0.5),
    (-0.5, 0.5, 0.5),
    (0.5, 0.5, 0.5),
    (0.5, 0.5, -0.5),
    # -Y
    (-0.5, -0.5, 0.5),
    (-0.5, -0.5, -0.5),
    (0.5, -0.5, -0.5),
    (0.5, -0.5, 0.5),
    # +Z
    (0.5, -0.5, 0.5),
    (0.5, 0.5, 0.5),
    (-0.5, 0.5, 0.5),
    (-0.5, -0.5, 0.5),
    # -Z
    (-0.5, -0.5, -0.5),
    (-0.5, 0.5, -0.5),
    (0.5, 0.5, -0.5),
    (0.5, -0.5, -0.5),
)
_CUBE_NORMALS = (
    (1, 0, 0),
    (1, 0, 0),
    (1, 0, 0),
    (1, 0, 0),
    (-1, 0, 0),
    (-1, 0, 0),
    (-1, 0, 0),
    (-1, 0, 0),
    (0, 1, 0),
    (0, 1, 0),
    (0, 1, 0),
    (0, 1, 0),
    (0, -1, 0),
    (0, -1, 0),
    (0, -1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, 1),
    (0, 0, 1),
    (0, 0, 1),
    (0, 0, -1),
    (0, 0, -1),
    (0, 0, -1),
    (0, 0, -1),
)
# UVs match _CUBE_POSITIONS. The +Y face maps U along +X and V along +Z so a
# floor slab can repeat a tile with KHR_texture_transform.
_CUBE_UVS = (
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
    (0.0, 0.0),
    (0.0, 1.0),
    (1.0, 1.0),
    (1.0, 0.0),
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
)
_CUBE_INDICES = (
    0,
    1,
    2,
    0,
    2,
    3,
    4,
    5,
    6,
    4,
    6,
    7,
    8,
    9,
    10,
    8,
    10,
    11,
    12,
    13,
    14,
    12,
    14,
    15,
    16,
    17,
    18,
    16,
    18,
    19,
    20,
    21,
    22,
    20,
    22,
    23,
)
# +Y top face only; vertical sides and bottom use a solid color (no tile texture).
_FLOOR_TOP_INDICES = _CUBE_INDICES[12:18]
_FLOOR_SHELL_INDICES = _CUBE_INDICES[:12] + _CUBE_INDICES[18:]

EQUIPMENT_CATEGORIES = (
    ("nodes", "node"),
    ("storage", "storage"),
    ("network", "network"),
    ("misc", "misc"),
)


def _mm(value):
    return value * MM_TO_M


def _three(values):
    return [float(values[0]), float(values[1]), float(values[2])]


def _quaternion_y_degrees(degrees):
    angle = math.radians(-degrees)
    half = angle / 2
    return [0.0, math.sin(half), 0.0, math.cos(half)]


def _rotate_y_point(x, y, z, degrees):
    if not degrees:
        return x, y, z
    angle = math.radians(-degrees)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return cos_a * x + sin_a * z, y, -sin_a * x + cos_a * z


def _data_uri_png(path):
    payload = path.read_bytes()
    return "data:image/png;base64," + base64.standard_b64encode(payload).decode("ascii")


# 12 edges of the unit cube, used as a 1px outline so devices stay distinct
# without shrinking the solid box.
_EDGE_POSITIONS = (
    (-0.5, -0.5, -0.5),
    (0.5, -0.5, -0.5),
    (0.5, 0.5, -0.5),
    (-0.5, 0.5, -0.5),
    (-0.5, -0.5, 0.5),
    (0.5, -0.5, 0.5),
    (0.5, 0.5, 0.5),
    (-0.5, 0.5, 0.5),
)
_EDGE_INDICES = (
    0,
    1,
    1,
    2,
    2,
    3,
    3,
    0,
    4,
    5,
    5,
    6,
    6,
    7,
    7,
    4,
    0,
    4,
    1,
    5,
    2,
    6,
    3,
    7,
)


def _build_binary_buffer():
    pos_bytes = b"".join(struct.pack("<fff", *p) for p in _CUBE_POSITIONS)
    norm_bytes = b"".join(struct.pack("<fff", *n) for n in _CUBE_NORMALS)
    uv_bytes = b"".join(struct.pack("<ff", *uv) for uv in _CUBE_UVS)
    idx_bytes = struct.pack("<" + "H" * len(_CUBE_INDICES), *_CUBE_INDICES)
    edge_pos_bytes = b"".join(struct.pack("<fff", *p) for p in _EDGE_POSITIONS)
    edge_idx_bytes = struct.pack("<" + "H" * len(_EDGE_INDICES), *_EDGE_INDICES)
    floor_top_idx_bytes = struct.pack(
        "<" + "H" * len(_FLOOR_TOP_INDICES), *_FLOOR_TOP_INDICES
    )
    floor_shell_idx_bytes = struct.pack(
        "<" + "H" * len(_FLOOR_SHELL_INDICES), *_FLOOR_SHELL_INDICES
    )
    blob = (
        pos_bytes
        + norm_bytes
        + uv_bytes
        + idx_bytes
        + edge_pos_bytes
        + edge_idx_bytes
        + floor_top_idx_bytes
        + floor_shell_idx_bytes
    )
    return (
        blob,
        len(pos_bytes),
        len(norm_bytes),
        len(uv_bytes),
        len(idx_bytes),
        len(edge_pos_bytes),
        len(edge_idx_bytes),
        len(floor_top_idx_bytes),
        len(floor_shell_idx_bytes),
    )


def _equipment_material(name, color, roughness):
    """PBR material for an equipment fill or border.

    three.js sets material.transparent only when alphaMode is BLEND. Opaque
    equipment omit the property and stay the glTF default OPAQUE.
    """
    material = {
        "name": name,
        "pbrMetallicRoughness": {
            "baseColorFactor": list(color),
            "metallicFactor": 0.0,
            "roughnessFactor": roughness,
        },
        "doubleSided": True,
    }
    if color[3] < 1.0:
        material["alphaMode"] = "BLEND"
    return material


class GltfInfrastructureDrawer:
    """Build a glTF 2.0 JSON document for one infrastructure."""

    def __init__(self, db, name, file, parameters):
        self.db = db
        self.file = file
        self.parameters = parameters
        self.infrastructure = None
        for infrastructure in self.db.infrastructures:
            if infrastructure.name == name:
                self.infrastructure = infrastructure
        if self.infrastructure is None:
            raise RacksDBDrawingError(
                f"Unable to find infrastructure {name} in database"
            )

    @property
    def _u_height_mm(self):
        return self.parameters.rack.u_height

    @property
    def _pane_width_mm(self):
        return self.parameters.rack.pane_width

    def _rack_inside_width_mm(self, rack):
        return rack.type.width - 2 * self._pane_width_mm

    def _equipment_width_mm(self, equipment):
        return equipment.type.width * self._rack_inside_width_mm(equipment.rack)

    def _equipment_center_local_mm(self, equipment):
        """Return the equipment box center in the parent rack node's frame.

        The named rack node is centered on the carcass, so corner-based placement
        (left inset, slot height, mid-depth) is shifted by half the rack size.
        """
        rack = equipment.rack
        eq_width = self._equipment_width_mm(equipment)
        left = self._pane_width_mm + equipment.position.width * eq_width
        center_x = left + eq_width / 2 - rack.type.width / 2
        bottom = equipment.position.height * self._u_height_mm
        height = equipment.type.height * self._u_height_mm
        center_y = bottom + height / 2 - rack.type.height / 2
        # Front face stays on the door (+Z); the inset is only at the rear.
        center_z = (EQUIPMENT_BACK_INSET_M / 2) / MM_TO_M
        return center_x, center_y, center_z

    def _equipment_depth_m(self, rack):
        depth = _mm(rack.type.depth) - EQUIPMENT_BACK_INSET_M
        return max(depth, EQUIPMENT_BACK_INSET_M)

    def _equipment_size_m(self, equipment):
        """Outer footprint of one device. The solid fills this box."""
        rack = equipment.rack
        return _three(
            (
                _mm(self._equipment_width_mm(equipment)),
                _mm(equipment.type.height * self._u_height_mm),
                self._equipment_depth_m(rack),
            )
        )

    def _equipment_gltf_colors(self, equipment, selected):
        colorset = find_equipment_colorset(self.parameters, equipment)
        if selected:
            return list(colorset.background), list(colorset.border)
        ghost = list(colorset.ghost)
        # Fully opaque ghost colors (the default #737373) would render solid.
        if ghost[3] == 1.0:
            ghost[3] = GHOST_EQUIPMENT_ALPHA
        return ghost, ghost

    def _add_equipment_geometry(
        self, nodes, eq_index, face_mesh_index, border_mesh_index, size_m
    ):
        """Fill the slot and stroke its edges.

        The solid is the full footprint, so neighboring devices touch. The
        outline is a line primitive on those same edges and does not open a gap.
        """
        self._add_mesh_child(nodes, eq_index, face_mesh_index, size_m)
        self._add_mesh_child(
            nodes,
            eq_index,
            border_mesh_index,
            size_m,
            extras={"category": "equipment-border"},
        )

    def _rack_size_m(self, rack):
        return _three(
            (_mm(rack.type.width), _mm(rack.type.height), _mm(rack.type.depth))
        )

    def _room_key(self, room):
        return room.datacenter.name, room.name

    def _rooms_ordered(self, racks):
        rooms = []
        seen = set()
        for part in self.infrastructure.layout:
            room = part.rack.room
            key = self._room_key(room)
            if key in seen:
                continue
            if any(self._room_key(rack.room) == key for rack in racks):
                rooms.append(room)
                seen.add(key)
        return rooms

    def _rows_for_room(self, room, racks):
        rows = []
        seen = set()
        for rack in racks:
            if rack.room is not room:
                continue
            row = rack.row
            if row.name not in seen:
                rows.append(row)
                seen.add(row.name)
        return rows

    def _racks_in_row(self, row, room, racks):
        return [
            rack
            for rack in racks
            if rack.row.name == row.name and rack.room is room
        ]

    def _iter_equipment(self, part):
        for attr, category in EQUIPMENT_CATEGORIES:
            for equipment in getattr(part, attr):
                yield equipment, category

    def _rack_panels(self, size_m, closed):
        """Panels of one rack carcass, in the rack node's local frame.

        Side panels use ``pane_width``, with the inner face stepped back by
        ``EQUIPMENT_SIDE_CLEARANCE_M`` so equipment sides are not coplanar with
        the wall. The outer face stays on the rack edge. Top and bottom are a
        thin shell inside the rack box. The door face (+Z) and the rear stay
        open unless ``closed``.
        """
        width, height, depth = size_m
        pane_outer = min(_mm(self._pane_width_mm), width / 2)
        clearance = min(EQUIPMENT_SIDE_CLEARANCE_M, pane_outer / 2)
        pane = pane_outer - clearance
        shell = min(SHELL_THICKNESS_M, depth / 2, height / 2)
        opening_w = max(width - 2 * pane, pane)
        opening_h = max(height - 2 * shell, shell)
        panels = [
            (
                "left",
                [pane, height, depth],
                [-width / 2 + pane / 2, 0.0, 0.0],
            ),
            (
                "right",
                [pane, height, depth],
                [width / 2 - pane / 2, 0.0, 0.0],
            ),
            (
                "top",
                [opening_w, shell, depth],
                [0.0, height / 2 - shell / 2, 0.0],
            ),
            (
                "bottom",
                [opening_w, shell, depth],
                [0.0, -height / 2 + shell / 2, 0.0],
            ),
        ]
        if closed:
            panels.append(
                (
                    "front",
                    [opening_w, opening_h, shell],
                    [0.0, 0.0, depth / 2 - shell / 2],
                )
            )
        return panels

    def _add_rack_carcass(self, nodes, rack_index, rack_mesh_index, size_m, closed):
        for part, scale, translation in self._rack_panels(size_m, closed):
            self._add_mesh_child(
                nodes,
                rack_index,
                rack_mesh_index,
                _three(scale),
                _three(translation),
                extras={"category": "rack-part", "part": part},
            )

    def _rack_center_row_m(self, rack):
        offset_mm = rack_slot_offset_x(self.db, rack, 1.0)
        size_m = self._rack_size_m(rack)
        return (
            _mm(offset_mm + rack.type.width / 2),
            size_m[1] / 2,
            size_m[2] / 2,
        )

    def _point_in_room_m(self, row, rack, local_x, local_y, local_z):
        if row.reversed:
            local_x, local_z = -local_x, -local_z
        rcx, rcy, rcz = self._rack_center_row_m(rack)
        x, y, z = local_x + rcx, local_y + rcy, local_z + rcz
        x, y, z = _rotate_y_point(x, y, z, row.position.rotation)
        x += _mm(row.position.width)
        z += _mm(row.position.depth)
        return x, y, z

    def _perforated_aisle_cells(self, row, rack):
        width_m = _mm(rack.type.width)
        depth_m = _mm(rack.type.depth)
        corners = []
        for local_x in (-width_m / 2, width_m / 2):
            for local_z in (depth_m / 2, depth_m / 2 + FLOOR_TILE_M):
                x, _, z = self._point_in_room_m(row, rack, local_x, 0.0, local_z)
                corners.append((x, z))
        min_x = min(c[0] for c in corners)
        max_x = max(c[0] for c in corners)
        min_z = min(c[1] for c in corners)
        max_z = max(c[1] for c in corners)
        ix_start = int(math.floor(min_x / FLOOR_TILE_M))
        ix_end = int(math.floor((max_x - 1e-9) / FLOOR_TILE_M))
        iz_start = int(math.floor(min_z / FLOOR_TILE_M))
        iz_end = int(math.floor((max_z - 1e-9) / FLOOR_TILE_M))
        cells = set()
        for ix in range(ix_start, ix_end + 1):
            for iz in range(iz_start, iz_end + 1):
                cx0 = ix * FLOOR_TILE_M
                cx1 = (ix + 1) * FLOOR_TILE_M
                cz0 = iz * FLOOR_TILE_M
                cz1 = (iz + 1) * FLOOR_TILE_M
                if cx1 <= min_x or cx0 >= max_x or cz1 <= min_z or cz0 >= max_z:
                    continue
                if (ix + iz) % 2 == 0:
                    cells.add((ix, iz))
        return cells

    def _add_mesh_child(
        self, nodes, parent_index, mesh_index, scale, translation=None, extras=None
    ):
        mesh_node = {"mesh": mesh_index, "scale": scale}
        if translation is not None:
            mesh_node["translation"] = translation
        if extras is not None:
            mesh_node["extras"] = extras
        nodes[parent_index]["children"].append(len(nodes))
        nodes.append(mesh_node)

    def draw(self):
        racks, _rack_rows = select_infrastructure_racks(
            self.infrastructure, self.parameters
        )
        if not racks:
            raise RacksDBDrawingError(
                "Unable to find racks to draw with filters provided in drawing "
                "parameters"
            )

        (
            blob,
            pos_len,
            norm_len,
            uv_len,
            idx_len,
            edge_pos_len,
            edge_idx_len,
            floor_top_idx_len,
            floor_shell_idx_len,
        ) = _build_binary_buffer()
        buffer_uri = (
            "data:application/octet-stream;base64,"
            + base64.standard_b64encode(blob).decode("ascii")
        )
        floor_solid_uri = _data_uri_png(FLOOR_TILE_SOLID_PNG)
        floor_perforated_uri = _data_uri_png(FLOOR_TILE_PERFORATED_PNG)

        pos_min = [-0.5, -0.5, -0.5]
        pos_max = [0.5, 0.5, 0.5]
        pos_offset = 0
        norm_offset = pos_len
        uv_offset = pos_len + norm_len
        idx_offset = uv_offset + uv_len
        edge_pos_offset = idx_offset + idx_len
        edge_idx_offset = edge_pos_offset + edge_pos_len
        floor_top_idx_offset = edge_idx_offset + edge_idx_len
        floor_shell_idx_offset = floor_top_idx_offset + floor_top_idx_len

        accessors = [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 24,
                "type": "VEC3",
                "min": pos_min,
                "max": pos_max,
            },
            {
                "bufferView": 1,
                "componentType": 5126,
                "count": 24,
                "type": "VEC3",
            },
            {
                "bufferView": 2,
                "componentType": 5126,
                "count": 24,
                "type": "VEC2",
            },
            {
                "bufferView": 3,
                "componentType": 5123,
                "count": 36,
                "type": "SCALAR",
            },
            {
                "bufferView": 4,
                "componentType": 5126,
                "count": 8,
                "type": "VEC3",
                "min": pos_min,
                "max": pos_max,
            },
            {
                "bufferView": 5,
                "componentType": 5123,
                "count": len(_EDGE_INDICES),
                "type": "SCALAR",
            },
            {
                "bufferView": 6,
                "componentType": 5123,
                "count": len(_FLOOR_TOP_INDICES),
                "type": "SCALAR",
            },
            {
                "bufferView": 7,
                "componentType": 5123,
                "count": len(_FLOOR_SHELL_INDICES),
                "type": "SCALAR",
            },
        ]
        buffer_views = [
            {"buffer": 0, "byteOffset": pos_offset, "byteLength": pos_len},
            {"buffer": 0, "byteOffset": norm_offset, "byteLength": norm_len},
            {"buffer": 0, "byteOffset": uv_offset, "byteLength": uv_len},
            {"buffer": 0, "byteOffset": idx_offset, "byteLength": idx_len},
            {"buffer": 0, "byteOffset": edge_pos_offset, "byteLength": edge_pos_len},
            {"buffer": 0, "byteOffset": edge_idx_offset, "byteLength": edge_idx_len},
            {
                "buffer": 0,
                "byteOffset": floor_top_idx_offset,
                "byteLength": floor_top_idx_len,
            },
            {
                "buffer": 0,
                "byteOffset": floor_shell_idx_offset,
                "byteLength": floor_shell_idx_len,
            },
        ]
        cube_vertex_attrs = {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2}
        primitive = {
            "attributes": cube_vertex_attrs,
            "indices": 3,
        }

        def floor_slab_primitives(top_material_index, shell_material_index):
            return [
                {
                    "attributes": cube_vertex_attrs,
                    "indices": 6,
                    "material": top_material_index,
                },
                {
                    "attributes": cube_vertex_attrs,
                    "indices": 7,
                    "material": shell_material_index,
                },
            ]
        meshes = [{"name": "rack", "primitives": [{**primitive, "material": 0}]}]
        materials = [
            {
                "name": "rack",
                "pbrMetallicRoughness": {
                    "baseColorFactor": RACK_COLOR,
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.85,
                },
                "doubleSided": True,
            },
        ]
        fill_mesh_by_color = {}
        border_mesh_by_color = {}

        def ensure_fill_mesh_index(fill_color):
            key = tuple(fill_color)
            cached = fill_mesh_by_color.get(key)
            if cached is not None:
                return cached
            material_index = len(materials)
            materials.append(
                _equipment_material(
                    "equipment-fill", fill_color, EQUIPMENT_FILL_ROUGHNESS
                )
            )
            mesh_index = len(meshes)
            meshes.append(
                {
                    "name": "equipment-fill",
                    "primitives": [{**primitive, "material": material_index}],
                }
            )
            fill_mesh_by_color[key] = mesh_index
            return mesh_index

        def ensure_border_mesh_index(border_color):
            key = tuple(border_color)
            cached = border_mesh_by_color.get(key)
            if cached is not None:
                return cached
            material_index = len(materials)
            materials.append(
                _equipment_material(
                    "equipment-border", border_color, EQUIPMENT_BORDER_ROUGHNESS
                )
            )
            mesh_index = len(meshes)
            meshes.append(
                {
                    "name": "equipment-border",
                    "primitives": [
                        {
                            "attributes": {"POSITION": 4},
                            "indices": 5,
                            "mode": 1,
                            "material": material_index,
                        }
                    ],
                }
            )
            border_mesh_by_color[key] = mesh_index
            return mesh_index
        images = [
            {"uri": floor_solid_uri, "mimeType": "image/png"},
            {"uri": floor_perforated_uri, "mimeType": "image/png"},
        ]
        samplers = [
            {
                "magFilter": 9729,
                "minFilter": 9987,
                "wrapS": 10497,
                "wrapT": 10497,
            }
        ]
        textures = [
            {"sampler": 0, "source": 0},
            {"sampler": 0, "source": 1},
        ]
        floor_side_material_index = len(materials)
        materials.append(
            {
                "name": "floor-side",
                "pbrMetallicRoughness": {
                    "baseColorFactor": FLOOR_SIDE_COLOR,
                    "metallicFactor": 0.0,
                    "roughnessFactor": FLOOR_ROUGHNESS,
                },
                "doubleSided": True,
            }
        )
        perforated_floor_material_index = len(materials)
        materials.append(
            {
                "name": "floor-perforated",
                "pbrMetallicRoughness": {
                    "baseColorFactor": FLOOR_BASE_COLOR_FACTOR,
                    "baseColorTexture": {
                        "index": 1,
                        "extensions": {"KHR_texture_transform": {"scale": [1.0, 1.0]}},
                    },
                    "metallicFactor": 0.0,
                    "roughnessFactor": FLOOR_ROUGHNESS,
                },
                "doubleSided": True,
            }
        )
        perforated_floor_mesh_index = len(meshes)
        meshes.append(
            {
                "name": "floor-perforated",
                "primitives": floor_slab_primitives(
                    perforated_floor_material_index, floor_side_material_index
                ),
            }
        )

        nodes = []
        scene_roots = []
        rack_mesh_index = 0
        room_offset_x_m = 0.0

        for room in self._rooms_ordered(racks):
            room_width_m = _mm(room.dimensions.width)
            room_depth_m = _mm(room.dimensions.depth)
            room_index = len(nodes)
            nodes.append(
                {
                    "name": room.name,
                    "translation": _three((room_offset_x_m, 0.0, 0.0)),
                    "children": [],
                    "extras": {
                        "category": "room",
                        "datacenter": room.datacenter.name,
                        "size": [room_width_m, 0.0, room_depth_m],
                    },
                }
            )
            scene_roots.append(room_index)
            room_offset_x_m += room_width_m + ROOM_GAP_M

            floor_material_index = len(materials)
            materials.append(
                {
                    "name": f"floor-{room.name}",
                    "pbrMetallicRoughness": {
                        "baseColorFactor": FLOOR_BASE_COLOR_FACTOR,
                        "baseColorTexture": {
                            "index": 0,
                            "extensions": {
                                "KHR_texture_transform": {
                                    "scale": [
                                        room_width_m / FLOOR_TILE_M,
                                        room_depth_m / FLOOR_TILE_M,
                                    ]
                                }
                            },
                        },
                        "metallicFactor": 0.0,
                        "roughnessFactor": FLOOR_ROUGHNESS,
                    },
                    "doubleSided": True,
                }
            )
            floor_mesh_index = len(meshes)
            meshes.append(
                {
                    "name": "floor",
                    "primitives": floor_slab_primitives(
                        floor_material_index, floor_side_material_index
                    ),
                }
            )
            floor_scale = [room_width_m, FLOOR_THICKNESS_M, room_depth_m]
            floor_center = [
                room_width_m / 2,
                -FLOOR_THICKNESS_M / 2 - FLOOR_CLEARANCE_M,
                room_depth_m / 2,
            ]
            self._add_mesh_child(
                nodes,
                room_index,
                floor_mesh_index,
                floor_scale,
                floor_center,
                extras={"category": "floor", "tile": FLOOR_TILE_M, "part": "slab"},
            )

            perforated_cells = set()
            row_racks = []

            for row in self._rows_for_room(room, racks):
                row_index = len(nodes)
                row_node = {
                    "name": row.name,
                    "translation": _three(
                        (_mm(row.position.width), 0.0, _mm(row.position.depth))
                    ),
                    "children": [],
                    "extras": {
                        "category": "row",
                        "reversed": bool(row.reversed),
                        "rotation": row.position.rotation,
                    },
                }
                rotation = row.position.rotation
                if rotation:
                    row_node["rotation"] = _quaternion_y_degrees(rotation)
                nodes[room_index]["children"].append(row_index)
                nodes.append(row_node)

                for rack in self._racks_in_row(row, room, racks):
                    row_racks.append((row, rack))
                    offset_mm = rack_slot_offset_x(self.db, rack, 1.0)
                    size_m = self._rack_size_m(rack)
                    center = _three(
                        (
                            _mm(offset_mm + rack.type.width / 2),
                            size_m[1] / 2,
                            size_m[2] / 2,
                        )
                    )
                    rack_index = len(nodes)
                    rack_node = {
                        "name": rack.name,
                        "translation": center,
                        "children": [],
                        "extras": {
                            "category": "rack",
                            "type": rack.type.id,
                            "in_infrastructure": rack_in_infrastructure(
                                self.infrastructure, rack
                            ),
                            "reversed": bool(row.reversed),
                            "slots": rack.type.slots,
                            "size": size_m,
                        },
                    }
                    if row.reversed:
                        rack_node["rotation"] = [0.0, 1.0, 0.0, 0.0]
                    nodes[row_index]["children"].append(rack_index)
                    nodes.append(rack_node)

                    in_infrastructure = rack_in_infrastructure(
                        self.infrastructure, rack
                    )
                    self._add_rack_carcass(
                        nodes,
                        rack_index,
                        rack_mesh_index,
                        size_m,
                        closed=not in_infrastructure,
                    )

                    if not in_infrastructure:
                        continue

                    part = infrastructure_part_for_rack(self.infrastructure, rack)
                    if part is None:
                        continue

                    for equipment, category in self._iter_equipment(part):
                        selected = equipment_matches_tags(equipment, self.parameters)
                        if not selected:
                            if not self.parameters.infrastructure.ghost_unselected:
                                continue
                        eq_size = self._equipment_size_m(equipment)
                        cx, cy, cz = self._equipment_center_local_mm(equipment)
                        eq_center = _three((_mm(cx), _mm(cy), _mm(cz)))
                        fill_color, border_color = self._equipment_gltf_colors(
                            equipment, selected
                        )
                        eq_index = len(nodes)
                        nodes.append(
                            {
                                "name": equipment.name,
                                "translation": eq_center,
                                "children": [],
                                "extras": {
                                    "category": category,
                                    "type": equipment.type.id,
                                    "tags": list(equipment.tags),
                                    "selected": selected,
                                    "size": eq_size,
                                    "rack": rack.name,
                                    "slot": {
                                        "u": equipment.position.height,
                                        "x": equipment.position.width,
                                    },
                                },
                            }
                        )
                        nodes[rack_index]["children"].append(eq_index)
                        fill_mesh_index = ensure_fill_mesh_index(fill_color)
                        border_mesh_index = ensure_border_mesh_index(border_color)
                        self._add_equipment_geometry(
                            nodes,
                            eq_index,
                            fill_mesh_index,
                            border_mesh_index,
                            eq_size,
                        )

            for row, rack in row_racks:
                perforated_cells |= self._perforated_aisle_cells(row, rack)

            vent_scale = [FLOOR_TILE_M, FLOOR_THICKNESS_M, FLOOR_TILE_M]
            vent_center_y = (
                -FLOOR_CLEARANCE_M + FLOOR_VENT_LIFT_M - FLOOR_THICKNESS_M / 2
            )
            for ix, iz in sorted(perforated_cells):
                self._add_mesh_child(
                    nodes,
                    room_index,
                    perforated_floor_mesh_index,
                    vent_scale,
                    [
                        (ix + 0.5) * FLOOR_TILE_M,
                        vent_center_y,
                        (iz + 0.5) * FLOOR_TILE_M,
                    ],
                    extras={"category": "floor", "part": "perforated"},
                )

        document = {
            "asset": {"version": "2.0"},
            "extensionsUsed": ["KHR_texture_transform"],
            "scene": 0,
            "scenes": [{"nodes": scene_roots}],
            "nodes": nodes,
            "meshes": meshes,
            "materials": materials,
            "textures": textures,
            "images": images,
            "samplers": samplers,
            "accessors": accessors,
            "bufferViews": buffer_views,
            "buffers": [{"byteLength": len(blob), "uri": buffer_uri}],
        }

        if hasattr(self.file, "write"):
            self.file.write(json.dumps(document, separators=(",", ":")).encode("utf-8"))
        else:
            with open(self.file, "w", encoding="utf-8") as fh:
                json.dump(document, fh, separators=(",", ":"))
