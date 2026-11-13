# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import logging
import math

import cairo

from .base2d import Drawer2D, ImagePoint
from ..errors import RacksDBDrawingError

logger = logging.getLogger(__name__)

# Float epsilon (in mm) used to absorb trigonometric rounding errors in
# collision detection, so that racks sharing an edge are not reported as
# colliding. This is not a physical tolerance.
EPSILON = 1e-6


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
            max(p[dim] for p in a) <= min(p[dim] for p in b) + EPSILON
            or max(p[dim] for p in b) <= min(p[dim] for p in a) + EPSILON
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
            # this axis are distances in mm comparable with EPSILON.
            axis = (axis[0] / length, axis[1] / length)
            min_a, max_a = _project(a, axis)
            min_b, max_b = _project(b, axis)
            if max_a <= min_b + EPSILON or max_b <= min_a + EPSILON:
                return False
    return True


class RackCoordinate:
    def __init__(self, x, y, width, height, angle):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle

    @property
    def _serialized(self):
        return [self.x, self.y, self.width, self.height, self.angle]


class RoomDrawer(Drawer2D):
    def __init__(
        self,
        db,
        name,
        file,
        output_format,
        parameters,
        coordinates_fh,
        coordinates_format,
    ):
        super().__init__(
            db,
            file,
            output_format,
            parameters,
            coordinates_fh,
            coordinates_format,
        )
        self.room = None
        for datacenter in self.db.datacenters:
            for room in datacenter.rooms:
                if room.name == name:
                    self.room = room
        if self.room is None:
            raise RacksDBDrawingError(f"Unable to find room {name} in database")
        # Calculated at draw time based on dimensions
        self.ratio = 0
        # Names of racks colliding with other racks, computed at draw time
        self._colliding_racks = set()

    def _racks_row_tl(self, row):
        return ImagePoint(
            self.parameters.margin.left + int(row.position.width * self.ratio),
            self.parameters.margin.top + int(row.position.depth * self.ratio),
        )

    def _rack_tl(self, rack):
        # Start from top-left corner of the rack row, which is (0,0) after
        # context matrix translation.
        tl = ImagePoint(0, 0)
        # Sum the width of all racks and empty slots in row before the current
        # rack.
        for width in self._rack_preceding_widths(rack):
            tl.x += int(width * self.ratio)
        return tl

    def _rack_footprint(self, rack):
        """Return the list of the 4 corners (x, y) of the rack in room
        coordinates, in mm."""
        offset = sum(self._rack_preceding_widths(rack))
        local = [
            (offset, 0),
            (offset + rack.type.width, 0),
            (offset + rack.type.width, rack.type.depth),
            (offset, rack.type.depth),
        ]
        # Rotate clockwise around row top-left corner (y axis points down),
        # consistently with cairo context rotation, then translate to row
        # position in room.
        angle = rack.row.position.rotation * math.pi / 180
        cos = math.cos(angle)
        sin = math.sin(angle)
        return [
            (
                rack.row.position.width + x * cos - y * sin,
                rack.row.position.depth + x * sin + y * cos,
            )
            for x, y in local
        ]

    def _check_collisions(self):
        """Detect collisions between racks in room, emit warnings and record
        names of colliding racks."""
        self._colliding_racks = set()
        # Build a flat list of (rack, footprint) tuples for all racks in the room, where
        # footprint is the list of the 4 corners of the rack in room coordinates (in
        # mm).
        footprints = [
            (rack, self._rack_footprint(rack))
            for row in self.room.rows
            for rack in row.racks
        ]
        # Compare each rack with all racks after it in the list, so that every pair
        # of racks is checked exactly once. For every overlapping pair, emit a warning
        # and record both racks names.
        for idx, (rack_a, footprint_a) in enumerate(footprints):
            for rack_b, footprint_b in footprints[idx + 1 :]:
                if polygons_overlap(footprint_a, footprint_b):
                    logger.warning(
                        "Collision detected in room %s between racks %s and %s",
                        self.room.name,
                        rack_a.name,
                        rack_b.name,
                    )
                    self._colliding_racks.add(rack_a.name)
                    self._colliding_racks.add(rack_b.name)

    def _draw_rack(self, rack):
        tl = self._rack_tl(rack)
        rack_width = int(rack.type.width * self.ratio)
        rack_height = int(rack.type.depth * self.ratio)

        colorset = self._find_rack_colorset(rack)

        # draw rack frame, in red if the rack collides with other racks and
        # collisions highlighting is enabled in drawing parameters
        if self.parameters.room.collisions and rack.name in self._colliding_racks:
            self.ctx.set_source_rgba(1, 0, 0, 1)  # red
            self.ctx.set_line_width(2)
        else:
            self.ctx.set_source_rgba(*colorset.frame)
            self.ctx.set_line_width(1)
        self.ctx.rectangle(
            tl.x - 0.5,
            tl.y - 0.5,
            rack_width + 1,
            rack_height + 1,
        )
        self.ctx.stroke()
        self.ctx.set_source_rgba(*colorset.frame)
        self.ctx.set_line_width(1)

        # draw rack front door
        if rack.row.reversed:
            self.ctx.rectangle(
                tl.x,
                tl.y,
                rack_width,
                (self.parameters.rack.door_depth * self.ratio),
            )
        else:
            self.ctx.rectangle(
                tl.x,
                tl.y + rack_height - (self.parameters.rack.door_depth * self.ratio),
                rack_width,
                (self.parameters.rack.door_depth * self.ratio),
            )
        self.ctx.fill()

        self._label_rack(rack)

    def _label_rack(self, rack):
        """Label rack with its name."""

        # Skip if racks_label drawing parameter is disabled
        if not self.parameters.room.racks_labels:
            return

        # Retrieve rack top-left corner and dimensions
        tl = self._rack_tl(rack)
        rack_width = int(rack.type.width * self.ratio)
        rack_height = int(rack.type.depth * self.ratio)

        self.ctx.set_source_rgba(0, 0, 0, 1)  # black
        if rack_height > rack_width:
            self.ctx.save()
            # If the rack row rotation angle is between 0 and 180, flip the text
            # to be right side up.
            if rack.row.position.rotation > 0 and rack.row.position.rotation < 180:
                self.ctx.move_to(tl.x, tl.y - 2 + rack_height)
                self.ctx.rotate(-math.pi / 2)
                self._print_text(rack.name, rack_width, rack_height)
            else:
                self.ctx.move_to(tl.x, tl.y + 2)
                self.ctx.rotate(math.pi / 2)
                self._print_text(rack.name, rack_width, rack_height, shift_y=True)
        else:
            self.ctx.move_to(tl.x, tl.y)
            self._print_text(rack.name, rack_width, rack_height)

        if rack_height > rack_width:
            self.ctx.restore()

    def _draw_racks_row(self, row):
        for rack in row.racks:
            self._draw_rack(rack)

    def draw(self):
        logger.debug(
            "Maximum dimensions: %d %d",
            self.parameters.dimensions.width,
            self.parameters.dimensions.height,
        )

        # Compute total white spaces in width and height
        width_whitespace = self.parameters.margin.left * 2
        height_whitespace = self.parameters.margin.top * 2

        # Deduce available space to draw in width and height
        available_width = self.parameters.dimensions.width - width_whitespace
        available_height = self.parameters.dimensions.height - height_whitespace
        logger.debug(
            "available draw area in pixels heights: %d width: %d",
            available_height,
            available_width,
        )

        self.ratio = min(
            available_width / self.room.dimensions.width,
            available_height / self.room.dimensions.depth,
        )

        logger.debug("Final ratio is: %f", self.ratio)

        self._check_collisions()

        # Compute final surface width and height
        surface_width = int(self.ratio * self.room.dimensions.width + width_whitespace)
        surface_height = int(
            self.ratio * self.room.dimensions.depth + height_whitespace
        )

        logger.debug("Final width: %d", surface_width)
        logger.debug("Final height: %d", surface_height)

        self.init_ctx(surface_width, surface_height)

        room_width = int(self.room.dimensions.width * self.ratio)
        room_depth = int(self.room.dimensions.depth * self.ratio)

        # draw room frame
        self.ctx.set_source_rgba(0.2, 0.2, 0.2, 1)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            self.parameters.margin.left - 0.5,
            self.parameters.margin.top - 0.5,
            room_width,
            room_depth,
        )
        self.ctx.stroke()

        # write room name
        self.ctx.set_source_rgba(0, 0, 0, 1)  # black
        self.ctx.select_font_face(
            "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )
        self.ctx.set_font_size(14)
        self.ctx.move_to(self.parameters.margin.left + 2, self.parameters.margin.top)
        self._print_text(
            f"Datacenter {self.room.datacenter.name} room {self.room.name}"
        )

        for row in self.room.rows:
            # Translate the context matrix to rack row top-left corner and
            # rotate it as per row rotation angle.
            self.ctx.save()
            tl = self._racks_row_tl(row)
            self.ctx.translate(tl.x, tl.y)
            self.ctx.rotate(row.position.rotation * math.pi / 180)
            self._draw_racks_row(row)
            self.ctx.restore()

        self.write()
