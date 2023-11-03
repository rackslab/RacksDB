# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import math

import cairo

from .base import Drawer, ImagePoint
from ..errors import RacksDBError

logger = logging.getLogger(__name__)


class RoomDrawer(Drawer):
    def __init__(self, db, name, file, output_format, parameters):
        super().__init__(db, file, output_format, parameters)
        self.room = None
        for datacenter in self.db.datacenters:
            for room in datacenter.rooms:
                if room.name == name:
                    self.room = room
        if self.room is None:
            raise RacksDBError(f"Unable to find room {name} in database")

    def _racks_row_tl(self, row):
        return ImagePoint(
            self.parameters.margin.left
            + int(row.position.width * self.parameters.room.scale),
            self.parameters.margin.top
            + int(row.position.depth * self.parameters.room.scale),
        )

    def _rack_tl(self, rack):
        # Start from top-left corner of the rack row, which is (0,0) after
        # context matrix translation.
        tl = ImagePoint(0, 0)
        # Sum the width of all racks in row before the current rack
        filled_slots = {}
        for row_rack in rack.row.racks:
            if row_rack.slot < rack.slot:
                tl.x += int(row_rack.type.width * self.parameters.room.scale)
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
                tl.x += int(last_rack_width * self.parameters.room.scale)
        return tl

    def _draw_rack(self, rack):
        tl = self._rack_tl(rack)
        rack_width = int(rack.type.width * self.parameters.room.scale)
        rack_height = int(rack.type.depth * self.parameters.room.scale)
        # draw rack frame
        self.ctx.set_source_rgb(0.4, 0.4, 0.4)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            tl.x,
            tl.y,
            rack_width,
            rack_height,
        )
        self.ctx.stroke()

        # draw rack front door
        if rack.row.reversed:
            self.ctx.rectangle(
                tl.x,
                tl.y,
                rack_width,
                (self.parameters.rack.door_depth * self.parameters.room.scale),
            )
        else:
            self.ctx.rectangle(
                tl.x,
                tl.y
                + rack_height
                - (self.parameters.rack.door_depth * self.parameters.room.scale),
                rack_width,
                (self.parameters.rack.door_depth * self.parameters.room.scale),
            )
        self.ctx.fill()

        # write rack name
        self.ctx.set_source_rgb(0, 0, 0)  # black
        if rack_height > rack_width:
            self.ctx.save()
            # If the rack row rotation angle is between 0 and 180, flip the text
            # to be right side up.
            if rack.row.position.rotation > 0 and rack.row.position.rotation < 180:
                self.ctx.move_to(tl.x + 15, tl.y - 2 + rack_height)
                self.ctx.rotate(-math.pi / 2)
            else:
                self.ctx.move_to(tl.x + 2, tl.y + 2)
                self.ctx.rotate(math.pi / 2)
        else:
            self.ctx.move_to(tl.x + 2, tl.y + 15)
        self.ctx.show_text(rack.name)
        if rack_height > rack_width:
            self.ctx.restore()

    def _draw_racks_row(self, row):
        for rack in row.racks:
            self._draw_rack(rack)

    def draw(self):
        room_width = int(self.room.dimensions.width * self.parameters.room.scale)
        room_depth = int(self.room.dimensions.depth * self.parameters.room.scale)

        width = room_width + 2 * self.parameters.margin.left
        height = room_depth + 2 * self.parameters.margin.top
        self.init_ctx(width, height)

        # draw room frame
        self.ctx.set_source_rgb(0.2, 0.2, 0.2)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            self.parameters.margin.left,
            self.parameters.margin.top,
            room_width,
            room_depth,
        )
        self.ctx.stroke()

        # write room name
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.select_font_face(
            "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )
        self.ctx.set_font_size(14)
        self.ctx.move_to(
            self.parameters.margin.left + 2, self.parameters.margin.top + 15
        )
        self.ctx.show_text(
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
