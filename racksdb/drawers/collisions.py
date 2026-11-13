# Copyright (c) 2026 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

"""Collisions detection between racks in rooms and between equipment in racks,
shared by 2D and 3D drawers."""

import logging
import math

logger = logging.getLogger(__name__)

# Float epsilon (in mm) used to absorb trigonometric rounding errors in
# collision detection, so that racks sharing an edge are not reported as
# colliding. This is not a physical tolerance.
POLYGON_EPSILON = 1e-6


def _project(polygon, axis):
    """Project polygon points on the line passing through the origin (0, 0) in the
    direction of the unit vector axis (x, y). Each projection is the dot product of
    the point with axis, ie. the signed distance from the origin to the point
    shadow on this line. Return the min and max projections, ie. the interval
    covered by the polygon shadow on this line."""
    values = [point[0] * axis[0] + point[1] * axis[1] for point in polygon]
    return min(values), max(values)


def polygons_overlap(a, b):
    """Return True if convex polygons a and b (lists of (x, y) points) strictly
    overlap, using the separating axis theorem. Polygons only touching on an
    edge or a corner are not considered overlapping."""
    # Quick check on axis-aligned bounding boxes: on each dimension (0 for x, 1 for
    # y), if the maximum coordinate of a polygon is lower than (or equal to) the
    # minimum coordinate of the other polygon, their bounding boxes are disjoint and
    # the polygons cannot overlap. This avoids the more expensive check below for
    # most pairs of distant polygons.
    for dim in (0, 1):
        if (
            max(p[dim] for p in a) <= min(p[dim] for p in b) + POLYGON_EPSILON
            or max(p[dim] for p in b) <= min(p[dim] for p in a) + POLYGON_EPSILON
        ):
            return False
    # Separating axis theorem: two convex polygons do not overlap if and only if
    # there is an axis on which their projections are disjoint, and it is enough to
    # test the axes perpendicular to the edges of both polygons. For each edge,
    # compute its unit normal (ie. perpendicular) vector, project all points of both
    # polygons on this axis and compare the resulting intervals. If they are disjoint
    # (or only touch), the axis separates the polygons and they do not overlap. If no
    # separating axis is found, the polygons overlap.
    for polygon in (a, b):
        for idx, point in enumerate(polygon):
            # Get the following point (x, y) in polygon, wrapping around to the first
            # point after the last one, so that point -> next_point is the polygon
            # edge that closes the shape.
            next_point = polygon[(idx + 1) % len(polygon)]
            # Compute the normal vector (x, y) of the edge, perpendicular to it. For an
            # edge vector (dx, dy) = next_point - point, the normal vector is the edge
            # vector rotated by 90°, ie. (-dy, dx).
            axis = (point[1] - next_point[1], next_point[0] - point[0])
            # Compute the length of the normal vector, ie. sqrt(x² + y²), equal to the
            # length of the edge.
            length = math.hypot(*axis)
            # Skip degenerated zero-length edges, when two consecutive points are
            # identical.
            if length == 0:
                continue
            # Normalize the normal vector, ie. divide it by its length to get a unit
            # vector (x, y) of length 1 in the same direction, so that projections on
            # this axis are distances in mm comparable with POLYGON_EPSILON.
            axis = (axis[0] / length, axis[1] / length)
            min_a, max_a = _project(a, axis)
            min_b, max_b = _project(b, axis)
            if max_a <= min_b + POLYGON_EPSILON or max_b <= min_a + POLYGON_EPSILON:
                return False
    return True


# Float epsilon used to absorb rounding errors on equipment fractional widths (eg.
# third of rack width) in collision detection, so that equipment just next to each
# other are not reported as colliding. This is not a physical tolerance.
EQUIPMENT_EPSILON = 1e-9


def _equipment_extent(equipment):
    """Return the tuple (bottom, top, left, right) of the space occupied by the
    equipment in its rack. Bottom and top are expressed in rack units relatively to
    the rack first slot, left and right are expressed as fractions of the rack
    width."""
    bottom = equipment.position.height
    left = equipment.position.width * equipment.type.width
    return (
        bottom,
        bottom + equipment.type.height,
        left,
        left + equipment.type.width,
    )


def equipment_overlap(a, b):
    """Return True if equipment a and b, assumed to be in the same rack, strictly
    overlap. Equipment only sharing a border (ie. stacked or side by side) are not
    considered overlapping."""
    a_bottom, a_top, a_left, a_right = _equipment_extent(a)
    b_bottom, b_top, b_left, b_right = _equipment_extent(b)
    return (
        a_bottom < b_top - EQUIPMENT_EPSILON
        and b_bottom < a_top - EQUIPMENT_EPSILON
        and a_left < b_right - EQUIPMENT_EPSILON
        and b_left < a_right - EQUIPMENT_EPSILON
    )


def colliding_equipment(racks):
    """Detect collisions between equipment in the given racks, emit warnings and
    return the set of names of colliding equipment. Equipment of all infrastructures
    are considered, not only the equipment of a specific infrastructure."""
    result = set()
    for rack in racks:
        equipments = rack.equipment
        # Compare each equipment with all equipment after it in the list, so that
        # every pair of equipment is checked exactly once.
        for idx, equipment_a in enumerate(equipments):
            for equipment_b in equipments[idx + 1 :]:
                if equipment_overlap(equipment_a, equipment_b):
                    logger.warning(
                        "Collision detected in rack %s between equipment %s "
                        "(infrastructure %s) and %s (infrastructure %s)",
                        rack.name,
                        equipment_a.name,
                        equipment_a.infrastructure.name,
                        equipment_b.name,
                        equipment_b.infrastructure.name,
                    )
                    result.add(equipment_a.name)
                    result.add(equipment_b.name)
    return result
