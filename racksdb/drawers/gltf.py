# Copyright (c) 2026 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

"""3D representations of infrastructures in glTF 2.0 format.

The scene uses meters, the Y axis is up. In rooms, the X axis follows room width and
the Z axis follows room depth, so that a scene viewed from above matches room maps.
The scene graph follows the database structure: room → racks row → rack →
equipment. Every node representing a database object is named after this object
and carries metadata in its extras. Geometry is attached to unnamed child nodes, so
that nodes of database objects are never scaled.
"""

import base64
from functools import lru_cache
import json
import logging
import math
from pathlib import Path
import struct
from typing import Optional

from .base import Drawer
from .collisions import colliding_equipment, polygons_overlap
from ..errors import RacksDBDrawingError

logger = logging.getLogger(__name__)

FORMATS = ("gltf", "glb")

MM_TO_M = 0.001

# Raised floor tiles
FLOOR_TILE_MM = 600
FLOOR_THICKNESS_M = 0.3
# Keep floor top surface slightly below racks bottom to avoid z-fighting.
FLOOR_CLEARANCE_M = 0.002
# Lift perforated tiles slightly above floor top surface to avoid z-fighting.
PERFORATED_TILE_LIFT_M = 0.0005
FLOOR_SIDE_COLOR = (0.34, 0.36, 0.40, 1.0)
FLOOR_ROUGHNESS = 0.8
# Horizontal gap between rooms when an infrastructure spans multiple rooms.
ROOMS_GAP_M = 2.0

# Racks and equipment
# Thickness of top and bottom sheets of racks carcass.
RACK_SHELL_THICKNESS_M = 0.008
# Inner faces of racks side panes are stepped back by this clearance, so they are
# not coplanar with equipment sides.
RACK_PANE_CLEARANCE_M = 0.001
RACK_ROUGHNESS = 0.85
# Equipment depth is not defined in database. Equipment are represented as deep
# as the rack minus this inset at the rear.
EQUIPMENT_REAR_INSET_M = 0.1
EQUIPMENT_ROUGHNESS = 1.0
# Ghost equipment opacity, when ghost color is fully opaque.
GHOST_ALPHA = 0.4
COLLISION_COLOR = (1.0, 0.0, 0.0, 1.0)

EQUIPMENT_CATEGORIES = (
    ("nodes", "node"),
    ("storage", "storage"),
    ("network", "network"),
    ("misc", "misc"),
)

ASSETS_DIR = Path(__file__).parent / "assets"

# glTF constants
GLTF_FLOAT = 5126
GLTF_UNSIGNED_SHORT = 5123
GLTF_ARRAY_BUFFER = 34962
GLTF_ELEMENT_ARRAY_BUFFER = 34963
GLTF_MODE_LINES = 1
GLTF_LINEAR = 9729
GLTF_LINEAR_MIPMAP_LINEAR = 9987
GLTF_REPEAT = 10497

GLB_MAGIC = 0x46546C67  # "glTF"
GLB_VERSION = 2
GLB_CHUNK_JSON = 0x4E4F534A  # "JSON"
GLB_CHUNK_BIN = 0x004E4942  # "BIN\0"

# Unit cube centered on origin, with flat normals: 4 vertices per face, 6 faces in
# order +X, -X, +Y, -Y, +Z, -Z.
_CUBE_FACES = (
    ((1, 0, 0), ((1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1))),
    ((-1, 0, 0), ((-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1))),
    ((0, 1, 0), ((-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1))),
    ((0, -1, 0), ((-1, -1, 1), (-1, -1, -1), (1, -1, -1), (1, -1, 1))),
    ((0, 0, 1), ((1, -1, 1), (1, 1, 1), (-1, 1, 1), (-1, -1, 1))),
    ((0, 0, -1), ((-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1))),
)
CUBE_POSITIONS = [
    tuple(c * 0.5 for c in vertex) for _, vertices in _CUBE_FACES for vertex in vertices
]
CUBE_NORMALS = [normal for normal, vertices in _CUBE_FACES for _ in vertices]
# Texture coordinates of the top (+Y) face are mapped on the X and Z axis, with
# (0, 0) on the (-X, -Z) corner, so floor textures are aligned on rooms origin.
# Other faces are not textured.
CUBE_UVS = [(x + 0.5, z + 0.5) for x, _, z in CUBE_POSITIONS]
CUBE_TOP_INDICES = [8, 9, 10, 8, 10, 11]
CUBE_INDICES = [
    index
    for face in range(6)
    for index in (
        4 * face,
        4 * face + 1,
        4 * face + 2,
        4 * face,
        4 * face + 2,
        4 * face + 3,
    )
]
CUBE_SHELL_INDICES = [index for index in CUBE_INDICES if index not in range(8, 12)]
# Unit cube corners and edges, to outline equipment.
EDGES_POSITIONS = [
    (x, y, z) for z in (-0.5, 0.5) for y in (-0.5, 0.5) for x in (-0.5, 0.5)
]
EDGES_INDICES = [
    *(0, 1, 2, 3, 4, 5, 6, 7),  # along X
    *(0, 2, 1, 3, 4, 6, 5, 7),  # along Y
    *(0, 4, 1, 5, 2, 6, 3, 7),  # along Z
]


def _m(value_mm: float) -> float:
    """Convert value in millimeters to meters."""
    return value_mm * MM_TO_M


def _linear(color):
    """Convert sRGB color with alpha channel, as defined in drawing parameters, into
    linear RGB as expected in glTF materials base color factors."""

    def channel(value):
        if value <= 0.04045:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    return tuple(round(channel(value), 6) for value in color[:3]) + (color[3],)


def _y_rotation(degrees: float):
    """Return quaternion of a rotation around the Y axis by the given angle in
    degrees, clockwise when viewed from above (ie. from +Y)."""
    half = math.radians(-degrees) / 2
    return [0.0, math.sin(half), 0.0, math.cos(half)]


def _round(value):
    """Recursively round floats in value to micrometers, to keep glTF JSON compact
    and free of floating point noise."""
    if isinstance(value, float):
        return round(value, 6) + 0.0  # + 0.0 turns -0.0 into 0.0
    if isinstance(value, list):
        return [_round(item) for item in value]
    if isinstance(value, dict):
        return {key: _round(item) for key, item in value.items()}
    return value


# The lru_cache decorator memoizes the function: the result of the first call with
# a given argument is stored and returned directly on subsequent calls with the
# same argument. With maxsize=None, the cache is unbounded. It is used here to read
# floor textures files from disk only once per process, as they are embedded in
# every generated glTF file (ie. on every request in REST API). The equivalent
# functools.cache decorator is not used as it requires Python >= 3.9.
@lru_cache(maxsize=None)
def _asset(name: str) -> bytes:
    return (ASSETS_DIR / name).read_bytes()


class GltfBuilder:
    """Assemble a glTF 2.0 document with a single binary buffer, serialized either in
    a glTF JSON file with the buffer embedded as data URI or in a GLB binary file."""

    def __init__(self):
        self.blob = bytearray()
        self.buffer_views = []
        self.accessors = []
        self.images = []
        self.samplers = []
        self.textures = []
        self.materials = []
        self.meshes = []
        self.nodes = []
        self.roots = []
        self.extensions_used = set()
        self._materials_cache = {}

    def add_buffer_view(self, data: bytes, target: Optional[int] = None) -> int:
        # Align all buffer views on 4 bytes boundaries, as required for vertex
        # attributes.
        self.blob.extend(b"\x00" * (-len(self.blob) % 4))
        buffer_view = {
            "buffer": 0,
            "byteOffset": len(self.blob),
            "byteLength": len(data),
        }
        if target is not None:
            buffer_view["target"] = target
        self.blob.extend(data)
        self.buffer_views.append(buffer_view)
        return len(self.buffer_views) - 1

    def add_vectors(self, vectors, bounds: bool = False) -> int:
        """Add an accessor of float vectors (VEC2 or VEC3) and return its index.
        When bounds is True, min and max values are set on the accessor, as required
        for vertex positions."""
        size = len(vectors[0])
        data = b"".join(struct.pack(f"<{size}f", *vector) for vector in vectors)
        accessor = {
            "bufferView": self.add_buffer_view(data, GLTF_ARRAY_BUFFER),
            "componentType": GLTF_FLOAT,
            "count": len(vectors),
            "type": f"VEC{size}",
        }
        if bounds:
            accessor["min"] = [float(min(v[i] for v in vectors)) for i in range(size)]
            accessor["max"] = [float(max(v[i] for v in vectors)) for i in range(size)]
        self.accessors.append(accessor)
        return len(self.accessors) - 1

    def add_indices(self, indices) -> int:
        """Add an accessor of vertex indices and return its index."""
        data = struct.pack(f"<{len(indices)}H", *indices)
        self.accessors.append(
            {
                "bufferView": self.add_buffer_view(data, GLTF_ELEMENT_ARRAY_BUFFER),
                "componentType": GLTF_UNSIGNED_SHORT,
                "count": len(indices),
                "type": "SCALAR",
            }
        )
        return len(self.accessors) - 1

    def add_texture(self, png: bytes) -> int:
        """Add repeated texture with the given PNG image and return its index."""
        if not self.samplers:
            self.samplers.append(
                {
                    "magFilter": GLTF_LINEAR,
                    "minFilter": GLTF_LINEAR_MIPMAP_LINEAR,
                    "wrapS": GLTF_REPEAT,
                    "wrapT": GLTF_REPEAT,
                }
            )
        self.images.append(
            {"bufferView": self.add_buffer_view(png), "mimeType": "image/png"}
        )
        self.textures.append({"sampler": 0, "source": len(self.images) - 1})
        return len(self.textures) - 1

    def add_material(
        self,
        name: str,
        color,
        roughness: float,
        texture: Optional[int] = None,
        texture_scale=None,
    ) -> int:
        """Add PBR material with given linear RGBA color and return its index.
        Identical materials are added only once."""
        key = (name, tuple(color), roughness, texture, texture_scale)
        if key in self._materials_cache:
            return self._materials_cache[key]
        pbr = {
            "baseColorFactor": list(color),
            "metallicFactor": 0.0,
            "roughnessFactor": roughness,
        }
        if texture is not None:
            pbr["baseColorTexture"] = {"index": texture}
            if texture_scale is not None:
                pbr["baseColorTexture"]["extensions"] = {
                    "KHR_texture_transform": {"scale": list(texture_scale)}
                }
                self.extensions_used.add("KHR_texture_transform")
        material = {"name": name, "pbrMetallicRoughness": pbr, "doubleSided": True}
        if color[3] < 1.0:
            material["alphaMode"] = "BLEND"
        self.materials.append(material)
        self._materials_cache[key] = len(self.materials) - 1
        return self._materials_cache[key]

    def add_mesh(self, name: str, primitives) -> int:
        self.meshes.append({"name": name, "primitives": primitives})
        return len(self.meshes) - 1

    def add_node(self, node: dict, parent: Optional[int] = None) -> int:
        """Add node, as a child of parent node or as a scene root if parent is None,
        and return its index."""
        self.nodes.append(_round(node))
        index = len(self.nodes) - 1
        if parent is None:
            self.roots.append(index)
        else:
            self.nodes[parent].setdefault("children", []).append(index)
        return index

    def _document(self, buffer: dict) -> dict:
        document = {
            "asset": {"version": "2.0", "generator": "RacksDB"},
            "scene": 0,
            "scenes": [{"nodes": self.roots}],
            "nodes": self.nodes,
            "meshes": self.meshes,
            "materials": self.materials,
            "accessors": self.accessors,
            "bufferViews": self.buffer_views,
            "buffers": [buffer],
        }
        if self.textures:
            document["samplers"] = self.samplers
            document["images"] = self.images
            document["textures"] = self.textures
        if self.extensions_used:
            document["extensionsUsed"] = sorted(self.extensions_used)
        return document

    def gltf(self) -> bytes:
        """Return glTF JSON document with binary buffer embedded as data URI."""
        uri = "data:application/octet-stream;base64," + base64.b64encode(
            self.blob
        ).decode("ascii")
        return json.dumps(
            self._document({"byteLength": len(self.blob), "uri": uri}),
            separators=(",", ":"),
        ).encode()

    def glb(self) -> bytes:
        """Return GLB binary file, with the JSON chunk padded with spaces and the
        binary chunk padded with zeros to 4 bytes boundaries."""
        content = json.dumps(
            self._document({"byteLength": len(self.blob)}), separators=(",", ":")
        ).encode()
        content += b" " * (-len(content) % 4)
        blob = bytes(self.blob) + b"\x00" * (-len(self.blob) % 4)
        length = 12 + 8 + len(content) + 8 + len(blob)
        return b"".join(
            [
                struct.pack("<III", GLB_MAGIC, GLB_VERSION, length),
                struct.pack("<II", len(content), GLB_CHUNK_JSON),
                content,
                struct.pack("<II", len(blob), GLB_CHUNK_BIN),
                blob,
            ]
        )


class GltfInfrastructureDrawer(Drawer):
    """Generate 3D representation of an infrastructure in glTF 2.0 format, with all
    the rooms and racks used by this infrastructure."""

    def __init__(
        self,
        db,
        name,
        file,
        output_format,
        parameters,
        coordinates_fh=None,
        coordinates_format=None,
    ):
        super().__init__(db, file, output_format, parameters)
        if output_format not in FORMATS:
            raise RacksDBDrawingError(f"Unsupported 3D format {output_format}")
        if coordinates_fh is not None:
            raise RacksDBDrawingError(
                f"Coordinates are not supported with {output_format} format"
            )
        self.infrastructure = self._find_infrastructure(name)
        self.builder = None
        # Names of racks used by the infrastructure, computed at draw time
        self._infrastructure_racks = set()
        self._colliding_equipment = set()

    # Geometry

    def _init_geometry(self):
        """Add shared unit cube meshes accessors and floor textures in builder."""
        builder = self.builder
        positions = builder.add_vectors(CUBE_POSITIONS, bounds=True)
        normals = builder.add_vectors(CUBE_NORMALS)
        uvs = builder.add_vectors(CUBE_UVS)
        self._cube = {"POSITION": positions, "NORMAL": normals}
        self._textured_cube = {**self._cube, "TEXCOORD_0": uvs}
        self._cube_indices = builder.add_indices(CUBE_INDICES)
        self._cube_top_indices = builder.add_indices(CUBE_TOP_INDICES)
        self._cube_shell_indices = builder.add_indices(CUBE_SHELL_INDICES)
        self._edges = {"POSITION": builder.add_vectors(EDGES_POSITIONS, bounds=True)}
        self._edges_indices = builder.add_indices(EDGES_INDICES)
        self._floor_texture = builder.add_texture(_asset("floor-tile-solid.png"))
        self._perforated_texture = builder.add_texture(
            _asset("floor-tile-perforated.png")
        )
        self._floor_side_material = builder.add_material(
            "floor-side", _linear(FLOOR_SIDE_COLOR), FLOOR_ROUGHNESS
        )
        self._perforated_tile_mesh = builder.add_mesh(
            "perforated-tile",
            [
                {
                    "attributes": self._textured_cube,
                    "indices": self._cube_top_indices,
                    "material": builder.add_material(
                        "perforated-tile",
                        (1.0, 1.0, 1.0, 1.0),
                        FLOOR_ROUGHNESS,
                        texture=self._perforated_texture,
                    ),
                }
            ],
        )
        self._meshes_cache = {}

    def _box_mesh(self, name: str, color, roughness: float) -> int:
        """Return index of unit cube mesh with the given sRGB color, added once."""
        key = ("box", name, tuple(color))
        if key not in self._meshes_cache:
            material = self.builder.add_material(name, _linear(color), roughness)
            self._meshes_cache[key] = self.builder.add_mesh(
                name,
                [
                    {
                        "attributes": self._cube,
                        "indices": self._cube_indices,
                        "material": material,
                    }
                ],
            )
        return self._meshes_cache[key]

    def _edges_mesh(self, name: str, color) -> int:
        """Return index of unit cube edges mesh with the given sRGB color, added
        once."""
        key = ("edges", name, tuple(color))
        if key not in self._meshes_cache:
            material = self.builder.add_material(
                name, _linear(color), EQUIPMENT_ROUGHNESS
            )
            self._meshes_cache[key] = self.builder.add_mesh(
                name,
                [
                    {
                        "attributes": self._edges,
                        "indices": self._edges_indices,
                        "mode": GLTF_MODE_LINES,
                        "material": material,
                    }
                ],
            )
        return self._meshes_cache[key]

    def _add_geometry(self, parent, mesh, part, scale, translation=None):
        node = {"mesh": mesh, "scale": [float(value) for value in scale]}
        if translation is not None:
            node["translation"] = [float(value) for value in translation]
        node["extras"] = {"part": part}
        self.builder.add_node(node, parent)

    # Rooms and floor

    def _rooms(self):
        """Return the list of rooms of the represented racks, in the order of the
        infrastructure layout."""
        rooms = {}
        for rack in self.racks:
            rooms.setdefault((rack.datacenter.name, rack.room.name), rack.room)
        return list(rooms.values())

    def _room_racks(self, room):
        """Return the list of represented racks in the given room."""
        return [
            rack
            for rack in self.racks
            if rack.room.name == room.name
            and rack.datacenter.name == room.datacenter.name
        ]

    def _add_floor(self, parent, room):
        width = _m(room.dimensions.width)
        depth = _m(room.dimensions.depth)
        tile = _m(FLOOR_TILE_MM)
        material = self.builder.add_material(
            "floor",
            (1.0, 1.0, 1.0, 1.0),
            FLOOR_ROUGHNESS,
            texture=self._floor_texture,
            texture_scale=(round(width / tile, 6), round(depth / tile, 6)),
        )
        mesh = self.builder.add_mesh(
            "floor",
            [
                {
                    "attributes": self._textured_cube,
                    "indices": self._cube_top_indices,
                    "material": material,
                },
                {
                    "attributes": self._cube,
                    "indices": self._cube_shell_indices,
                    "material": self._floor_side_material,
                },
            ],
        )
        self._add_geometry(
            parent,
            mesh,
            "floor",
            (width, FLOOR_THICKNESS_M, depth),
            (width / 2, -FLOOR_CLEARANCE_M - FLOOR_THICKNESS_M / 2, depth / 2),
        )

    def _rack_polygon(self, rack, z_min: float, z_max: float):
        """Return the list of the 4 corners (x, z) in mm in room coordinates of the
        area covered by the rack width between z_min and z_max, in mm in the racks
        row depth axis."""
        offset = sum(self._rack_preceding_widths(rack))
        local = [
            (offset, z_min),
            (offset + rack.type.width, z_min),
            (offset + rack.type.width, z_max),
            (offset, z_max),
        ]
        angle = math.radians(rack.row.position.rotation)
        cos = math.cos(angle)
        sin = math.sin(angle)
        return [
            (
                rack.row.position.width + x * cos - z * sin,
                rack.row.position.depth + x * sin + z * cos,
            )
            for x, z in local
        ]

    def _rack_footprint(self, rack):
        """Return the rack footprint polygon in room coordinates, in mm."""
        return self._rack_polygon(rack, 0, rack.type.depth)

    def _rack_aisle(self, rack):
        """Return the polygon in room coordinates, in mm, of the tile-deep area in
        front of the rack door."""
        if rack.row.reversed:
            return self._rack_polygon(rack, -FLOOR_TILE_MM, 0)
        return self._rack_polygon(
            rack, rack.type.depth, rack.type.depth + FLOOR_TILE_MM
        )

    def _perforated_tiles(self, room, racks):
        """Return the sorted list of floor tiles (ix, iz) indexes that are perforated
        in the room. Perforated tiles are in front of racks doors, every other tile in
        checkerboard pattern, except tiles inside racks footprints or outside of the
        room."""
        footprints = [self._rack_footprint(rack) for rack in racks]
        max_ix = room.dimensions.width // FLOOR_TILE_MM
        max_iz = room.dimensions.depth // FLOOR_TILE_MM
        tiles = set()
        for rack in racks:
            aisle = self._rack_aisle(rack)
            xs = [point[0] for point in aisle]
            zs = [point[1] for point in aisle]
            for ix in range(
                max(math.floor(min(xs) / FLOOR_TILE_MM), 0),
                min(math.ceil(max(xs) / FLOOR_TILE_MM), max_ix),
            ):
                for iz in range(
                    max(math.floor(min(zs) / FLOOR_TILE_MM), 0),
                    min(math.ceil(max(zs) / FLOOR_TILE_MM), max_iz),
                ):
                    if (ix + iz) % 2 or (ix, iz) in tiles:
                        continue
                    x0, z0 = ix * FLOOR_TILE_MM, iz * FLOOR_TILE_MM
                    x1, z1 = x0 + FLOOR_TILE_MM, z0 + FLOOR_TILE_MM
                    if not polygons_overlap(
                        [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], aisle
                    ):
                        continue
                    # Small square around tile center, to check it is not under a
                    # rack.
                    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
                    center = [
                        (cx - 1, cz - 1),
                        (cx + 1, cz - 1),
                        (cx + 1, cz + 1),
                        (cx - 1, cz + 1),
                    ]
                    if any(polygons_overlap(center, fp) for fp in footprints):
                        continue
                    tiles.add((ix, iz))
        return sorted(tiles)

    def _add_perforated_tiles(self, parent, room, racks):
        tile = _m(FLOOR_TILE_MM)
        for ix, iz in self._perforated_tiles(room, racks):
            self._add_geometry(
                parent,
                self._perforated_tile_mesh,
                "perforated-tile",
                (tile, FLOOR_THICKNESS_M, tile),
                (
                    (ix + 0.5) * tile,
                    -FLOOR_CLEARANCE_M + PERFORATED_TILE_LIFT_M - FLOOR_THICKNESS_M / 2,
                    (iz + 0.5) * tile,
                ),
            )

    # Racks

    def _add_rack(self, parent, rack):
        width = _m(rack.type.width)
        height = _m(rack.type.height)
        depth = _m(rack.type.depth)
        offset = _m(sum(self._rack_preceding_widths(rack)))
        in_infrastructure = rack.name in self._infrastructure_racks
        node = {
            "name": rack.name,
            "translation": [offset + width / 2, height / 2, depth / 2],
            "extras": {
                "category": "rack",
                "type": rack.type.id,
                "tags": list(getattr(rack, "tags", [])),
                "infrastructure": in_infrastructure,
                "size": [width, height, depth],
            },
        }
        # Racks doors face +Z, rotate racks of reversed rows by 180° around Y.
        if rack.row.reversed:
            node["rotation"] = [0.0, 1.0, 0.0, 0.0]
        index = self.builder.add_node(node, parent)

        mesh = self._box_mesh(
            "rack", self._find_rack_colorset(rack).frame, RACK_ROUGHNESS
        )
        pane = min(_m(self.parameters.rack.pane_width), width / 2)
        pane -= min(RACK_PANE_CLEARANCE_M, pane / 2)
        shell = min(RACK_SHELL_THICKNESS_M, height / 2, depth / 2)
        inner_width = width - 2 * pane
        panels = [
            ("left", (pane, height, depth), (-width / 2 + pane / 2, 0, 0)),
            ("right", (pane, height, depth), (width / 2 - pane / 2, 0, 0)),
            ("top", (inner_width, shell, depth), (0, height / 2 - shell / 2, 0)),
            ("bottom", (inner_width, shell, depth), (0, -height / 2 + shell / 2, 0)),
        ]
        # Rack is not in the infrastructure, it is represented because other_racks
        # is enabled. Close its door, as in 2D infrastructure diagrams.
        if not in_infrastructure:
            panels.append(
                (
                    "door",
                    (inner_width, height - 2 * shell, shell),
                    (0, 0, depth / 2 - shell / 2),
                )
            )
        for part, scale, translation in panels:
            self._add_geometry(index, mesh, part, scale, translation)

        if in_infrastructure:
            for part in self.infrastructure.layout:
                if part.rack.name != rack.name:
                    continue
                for attribute, category in EQUIPMENT_CATEGORIES:
                    for equipment in getattr(part, attribute):
                        self._add_equipment(index, rack, equipment, category)

    # Equipment

    def _add_equipment(self, parent, rack, equipment, category):
        selected = self._equipment_selected(equipment)
        if not selected and not self.parameters.infrastructure.ghost_unselected:
            return
        u_height = self.parameters.rack.u_height
        pane = self.parameters.rack.pane_width
        rack_width = rack.type.width
        width = equipment.type.width * (rack_width - 2 * pane)
        height = equipment.type.height * u_height
        left = pane + equipment.position.width * width
        bottom = equipment.position.height * u_height
        depth = max(_m(rack.type.depth) - EQUIPMENT_REAR_INSET_M, 0.01)
        size = [_m(width), _m(height), depth]
        colliding = equipment.name in self._colliding_equipment

        colorset = self._find_equipment_colorset(equipment)
        if selected:
            fill = colorset.background
            border = colorset.border
        else:
            # Fully opaque ghost color would render solid ghosts.
            fill = border = colorset.ghost
            if fill[3] == 1.0:
                fill = border = fill[:3] + (GHOST_ALPHA,)
        if colliding and self.parameters.infrastructure.collisions:
            border = COLLISION_COLOR

        index = self.builder.add_node(
            {
                "name": equipment.name,
                # Equipment front face is aligned with the rack door, at +Z.
                "translation": [
                    _m(left + width / 2 - rack_width / 2),
                    _m(bottom + height / 2) - _m(rack.type.height) / 2,
                    (_m(rack.type.depth) - depth) / 2,
                ],
                "extras": {
                    "category": category,
                    "type": equipment.type.id,
                    "tags": list(equipment.tags),
                    "rack": rack.name,
                    "slot": {
                        "height": equipment.position.height,
                        "width": equipment.position.width,
                    },
                    "selected": selected,
                    "colliding": colliding,
                    "size": size,
                },
            },
            parent,
        )
        self._add_geometry(
            index, self._box_mesh("equipment", fill, EQUIPMENT_ROUGHNESS), "body", size
        )
        self._add_geometry(
            index, self._edges_mesh("equipment-edges", border), "edges", size
        )

    # Main

    def draw(self):
        self.racks, _ = self._select_infrastructure_racks(self.infrastructure)
        self._infrastructure_racks = {
            part.rack.name for part in self.infrastructure.layout
        }
        self._colliding_equipment = colliding_equipment(self.racks)

        self.builder = GltfBuilder()
        self._init_geometry()

        room_offset = 0.0
        for room in self._rooms():
            room_racks = self._room_racks(room)
            room_index = self.builder.add_node(
                {
                    "name": room.name,
                    "translation": [room_offset, 0.0, 0.0],
                    "extras": {
                        "category": "room",
                        "datacenter": room.datacenter.name,
                        "size": [
                            _m(room.dimensions.width),
                            0.0,
                            _m(room.dimensions.depth),
                        ],
                    },
                }
            )
            room_offset += _m(room.dimensions.width) + ROOMS_GAP_M
            self._add_floor(room_index, room)
            self._add_perforated_tiles(room_index, room, room_racks)

            rows = {}
            for rack in room_racks:
                rows.setdefault(rack.row.name, rack.row)
            for row in rows.values():
                row_node = {
                    "name": row.name,
                    "translation": [
                        _m(row.position.width),
                        0.0,
                        _m(row.position.depth),
                    ],
                    "extras": {"category": "row", "reversed": bool(row.reversed)},
                }
                if row.position.rotation:
                    row_node["rotation"] = _y_rotation(row.position.rotation)
                row_index = self.builder.add_node(row_node, room_index)
                for rack in room_racks:
                    if rack.row.name == row.name:
                        self._add_rack(row_index, rack)

        if self.output_format == "glb":
            content = self.builder.glb()
        else:
            content = self.builder.gltf()
        if hasattr(self.file, "write"):
            self.file.write(content)
        else:
            with open(self.file, "wb") as fh:
                fh.write(content)
