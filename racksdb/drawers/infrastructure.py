#!/usr/bin/env python3
#
# Copyright (C) 2022 Rackslab
#
# This file is part of RacksDB.
#
# RacksDB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RacksDB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RacksDB.  If not, see <https://www.gnu.org/licenses/>.

import logging
import math

import cairo

from .base import Drawer, ImagePoint
from ..errors import RacksDBError

logger = logging.getLogger(__name__)


class InfrastructureDrawer(Drawer):

    SCALE = 0.40  # 1mm to pixel
    MARGIN_TOP = 30
    ROW_LABEL_OFFSET = 20
    RACK_LABEL_OFFSET = 20
    RACK_OFFSET = 10
    MARGIN_LEFT = 30
    RACK_U_HEIGHT = 44.45 * SCALE
    RACK_HEIGHT = RACK_U_HEIGHT * 42
    RACK_ROW_HEIGHT = (
        RACK_HEIGHT + ROW_LABEL_OFFSET + RACK_LABEL_OFFSET + RACK_OFFSET
    )
    RACK_PANE_WIDTH = 10
    RACK_SPACING = 3  # space between racks

    def __init__(self, db, name, output_format):
        super().__init__(db, name, output_format)
        self.infrastructure = None
        for infrastructure in self.db.infrastructures:
            if infrastructure.name == name:
                self.infrastructure = infrastructure
        if self.infrastructure is None:
            raise RacksDBError(
                f"Unable to find infrastructure {name} in database"
            )

    def _rack_row_tl(self, row_index) -> ImagePoint:
        return ImagePoint(
            self.MARGIN_LEFT,
            self.MARGIN_TOP
            + self.ROW_LABEL_OFFSET
            + self.RACK_ROW_HEIGHT * row_index,
        )

    def _rack_tl(self, row_index, rack) -> ImagePoint:
        tl = self._rack_row_tl(row_index)

        # Sum the width of all racks in row before the current rack
        for row_rack in rack.row.racks:
            if row_rack.slot < rack.slot:
                tl.x += (
                    int(row_rack.type.width * self.SCALE) + self.RACK_SPACING
                )
        tl.y += self.RACK_LABEL_OFFSET + self.RACK_OFFSET
        return tl

    def _equipment_tl(self, row_index, rack, equipment) -> ImagePoint:
        tl = self._rack_tl(row_index, rack)

        equipment_height_slot = (
            equipment._first.slot
            + math.floor(
                (equipment.slot - equipment._first.slot) * equipment.type.width
            )
            * equipment.type.height
        )
        equipment_width_slot = (equipment.slot - equipment._first.slot) % (
            1 / equipment.type.width
        )

        logger.debug(
            "Equipment %s calculated slots → height: %d width: %d",
            equipment.name,
            equipment_height_slot,
            equipment_width_slot,
        )

        tl.x += (
            self.RACK_PANE_WIDTH
            + equipment_width_slot
            * equipment.type.width
            * (
                int(equipment.rack.type.width * self.SCALE)
                - 2 * self.RACK_PANE_WIDTH
            )
        )
        tl.y += (
            42 - equipment.type.height - equipment_height_slot
        ) * self.RACK_U_HEIGHT
        return tl

    def _draw_rack_equipment(self, row_index, rack, equipment):
        logger.debug(
            "Drawing equipment %s in rack %s",
            equipment.name,
            rack.name,
        )

        # top left of equipment
        tl = self._equipment_tl(row_index, rack, equipment)

        equipment_width = equipment.type.width * (
            int(equipment.rack.type.width * self.SCALE)
            - 2 * self.RACK_PANE_WIDTH
        )
        equipment_height = int(equipment.type.height * self.RACK_U_HEIGHT)

        # draw equipment background
        self.ctx.set_source_rgb(0.6, 0.6, 0.6)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            tl.x,
            tl.y,
            equipment_width,
            equipment_height,
        )
        self.ctx.fill()

        # draw equipment frame
        self.ctx.set_source_rgb(0.2, 0.2, 0.2)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            tl.x,
            tl.y,
            equipment_width,
            equipment_height,
        )
        self.ctx.stroke()

        # Write equipment name, rotate the text if height > width
        if equipment_height > equipment_width:
            self.ctx.move_to(tl.x + 2, tl.y + 2)
            self.ctx.save()
            self.ctx.rotate(math.pi / 2)
        else:
            self.ctx.move_to(tl.x + 2, tl.y + 15)
        self.ctx.show_text(equipment.name)
        if equipment_height > equipment_width:
            self.ctx.restore()

    def _draw_rack(self, row_index, rack):
        logger.debug("Drawing rack %s (%s)", rack.name, rack.slot)

        # top left of rack
        tl = self._rack_tl(row_index, rack)

        rack_width = rack.type.width * self.SCALE
        rack_height = rack.type.height * self.SCALE

        # write rack name
        self.ctx.move_to(tl.x, tl.y - self.RACK_OFFSET)
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.show_text(f"rack {rack.name}")

        # draw rack frame
        self.ctx.set_source_rgb(0.2, 0.2, 0.2)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            tl.x,
            tl.y,
            rack_width,
            rack_height,
        )
        self.ctx.stroke()

        # draw rack panes
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.rectangle(
            tl.x,
            tl.y,
            self.RACK_PANE_WIDTH,
            rack_height,
        )
        self.ctx.rectangle(
            tl.x + rack_width - self.RACK_PANE_WIDTH,
            tl.y,
            self.RACK_PANE_WIDTH,
            rack_height,
        )
        self.ctx.fill()

        # draw equipments in rack
        for part in self.infrastructure.layout:
            if part.rack is rack:
                for equipment in part.nodes + part.storage + part.network:
                    self._draw_rack_equipment(row_index, rack, equipment)

    def _draw_rack_row(self, index, row, racks):

        logger.debug("Drawing row %s", row.name)

        tl = self._rack_row_tl(index)

        # write row name
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.select_font_face(
            "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )
        self.ctx.set_font_size(14)
        self.ctx.move_to(tl.x, tl.y)
        self.ctx.show_text(f"row {row.name}")

        # iterate over the racks to draw racks in row
        for rack in racks:
            if rack.row is row:
                self._draw_rack(index, rack)

    def _draw_infrastructure(self, rack_rows, racks):
        for index, row in enumerate(rack_rows):
            self._draw_rack_row(index, row, racks)

    def draw(self):

        rack_rows = []
        racks = []

        # Get list of racks and rows used by the infrastructure
        for part in self.infrastructure.layout:
            if part.rack not in racks:
                racks.append(part.rack)
            if part.rack.row not in rack_rows:
                rack_rows.append(part.rack.row)

        # Sum all rows maximum rack height to calculate image height
        total_row_max_heights = 0
        for rack_row in rack_rows:
            row_max_height = 0
            for rack in rack_row.racks:
                row_max_height = max(row_max_height, rack.type.height)
            total_row_max_heights += row_max_height

        # Find the maximum rack x to calculate image width
        total_racks_widths = 0
        for rack in racks:
            tl = self._rack_tl(0, rack)
            x_tr = tl.x + int(rack.type.width * self.SCALE)
            total_racks_widths = max(total_racks_widths, x_tr)

        surface_width = total_racks_widths + self.MARGIN_LEFT
        surface_height = (
            2 * self.MARGIN_TOP
            + len(rack_rows)
            * (
                self.ROW_LABEL_OFFSET
                + self.RACK_LABEL_OFFSET
                + self.RACK_OFFSET
            )
            + int(total_row_max_heights * self.SCALE)
        )

        self.init_ctx(surface_width, surface_height)
        self._draw_infrastructure(rack_rows, racks)
        self.write()
