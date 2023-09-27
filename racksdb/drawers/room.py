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

    SCALE = 0.07  # 1mm to pixel
    MARGIN_TOP = 30
    MARGIN_LEFT = 30
    RACK_DOOR_DEPTH = int(50 * SCALE)

    def __init__(self, db, name, file, output_format):
        super().__init__(db, file, output_format)
        self.room = None
        for datacenter in self.db.datacenters:
            for room in datacenter.rooms:
                if room.name == name:
                    self.room = room
        if self.room is None:
            raise RacksDBError(f"Unable to find room {name} in database")

    def _racks_row_tl(self, row):
        return ImagePoint(
            self.MARGIN_LEFT + int(row.position.width * self.SCALE),
            self.MARGIN_TOP + int(row.position.depth * self.SCALE),
        )

    def _rack_tl(self, rack):
        # Start from top-left corner of the rack row, which is (0,0) after
        # context matrix translation.
        tl = ImagePoint(0, 0)
        # Sum the width of all racks in row before the current rack
        filled_slots = {}
        for row_rack in rack.row.racks:
            if row_rack.slot < rack.slot:
                tl.x += int(row_rack.type.width * self.SCALE)
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
                tl.x += int(last_rack_width * self.SCALE)
        return tl

    def _draw_rack(self, rack):
        tl = self._rack_tl(rack)
        rack_width = int(rack.type.width * self.SCALE)
        rack_height = int(rack.type.depth * self.SCALE)
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
                self.RACK_DOOR_DEPTH,
            )
        else:
            self.ctx.rectangle(
                tl.x,
                tl.y + rack_height - self.RACK_DOOR_DEPTH,
                rack_width,
                self.RACK_DOOR_DEPTH,
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
        room_width = int(self.room.dimensions.width * self.SCALE)
        room_depth = int(self.room.dimensions.depth * self.SCALE)

        width = room_width + 2 * self.MARGIN_LEFT
        height = room_depth + 2 * self.MARGIN_TOP
        self.init_ctx(width, height)

        # draw room frame
        self.ctx.set_source_rgb(0.2, 0.2, 0.2)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            self.MARGIN_LEFT,
            self.MARGIN_TOP,
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
        self.ctx.move_to(self.MARGIN_LEFT + 2, self.MARGIN_TOP + 15)
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
