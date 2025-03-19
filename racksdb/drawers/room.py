# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import math

import cairo

from .base import Drawer, ImagePoint
from ..errors import RacksDBDrawingError

logger = logging.getLogger(__name__)


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


class RoomDrawer(Drawer):
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

    def _racks_row_tl(self, row):
        return ImagePoint(
            self.parameters.margin.left + int(row.position.width * self.ratio),
            self.parameters.margin.top + int(row.position.depth * self.ratio),
        )

    def _rack_tl(self, rack):
        # Start from top-left corner of the rack row, which is (0,0) after
        # context matrix translation.
        tl = ImagePoint(0, 0)
        # Sum the width of all racks in row before the current rack
        filled_slots = {}
        for row_rack in rack.row.racks:
            if row_rack.slot < rack.slot:
                tl.x += int(row_rack.type.width * self.ratio)
                filled_slots[row_rack.slot] = row_rack
        # filling empty slots with previous rack width
        for slot in range(rack.slot):
            if slot not in filled_slots:
                logger.debug("Row %s slot %d is not filled", rack.row.name, slot)
                last_rack_width = 0
                reversed_slot = slot
                for reversed_slot in range(slot, 0, -1):
                    if reversed_slot in filled_slots:
                        last_rack_width = filled_slots[reversed_slot].type.width
                        break
                if not (last_rack_width):
                    last_rack_width = self.db.types.racks.first().width
                tl.x += int(last_rack_width * self.ratio)
        return tl

    def _draw_rack(self, rack):
        tl = self._rack_tl(rack)
        rack_width = int(rack.type.width * self.ratio)
        rack_height = int(rack.type.depth * self.ratio)

        colorset = self._find_rack_colorset(rack)

        # draw rack frame
        self.ctx.set_source_rgba(*colorset.frame)
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            tl.x - 0.5,
            tl.y - 0.5,
            rack_width + 1,
            rack_height + 1,
        )
        self.ctx.stroke()

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
