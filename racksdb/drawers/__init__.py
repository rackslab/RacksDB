# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from .room import RoomDrawer
from .infrastructure import InfrastructureDrawer
from .axonometric_infrastructure import AxonometricInfrastructureDrawer
from .gltf import GltfInfrastructureDrawer, FORMATS as GLTF_FORMATS
from ..errors import RacksDBDrawingError


def drawer_class(entity, output_format, parameters, coordinates=False):
    """Return the drawer class to represent the given entity type in the given output
    format with the drawing parameters. Raise RacksDBDrawingError if this combination
    is not supported."""
    if output_format in GLTF_FORMATS:
        if entity != "infrastructure":
            raise RacksDBDrawingError(
                f"Format {output_format} is only supported for infrastructures"
            )
        if coordinates:
            raise RacksDBDrawingError(
                f"Coordinates are not supported with {output_format} format"
            )
        return GltfInfrastructureDrawer
    if entity == "infrastructure":
        if parameters.axonometric.enabled:
            return AxonometricInfrastructureDrawer
        return InfrastructureDrawer
    if entity == "room":
        return RoomDrawer
    raise RacksDBDrawingError(f"Unable to draw entity {entity}")


__all__ = [
    "RoomDrawer",
    "InfrastructureDrawer",
    "AxonometricInfrastructureDrawer",
    "GltfInfrastructureDrawer",
    "GLTF_FORMATS",
    "drawer_class",
]
