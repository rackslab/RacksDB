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


class InfrastructureDrawer(Drawer):

    SCALE = 0.40  # 1mm to pixel
    MARGIN_TOP = 30
    ROW_LABEL_OFFSET = 20
    RACK_LABEL_OFFSET = 20
    RACK_OFFSET = 10
    MARGIN_LEFT = 30
    RACK_U_HEIGHT = 44.45 * SCALE
    RACK_PANE_WIDTH = 10
    RACK_SPACING = 3  # space between racks

    def __init__(self, db, name, file, output_format):
        super().__init__(db, file, output_format)
        self.infrastructure = None
        for infrastructure in self.db.infrastructures:
            if infrastructure.name == name:
                self.infrastructure = infrastructure
        if self.infrastructure is None:
            raise RacksDBError(f"Unable to find infrastructure {name} in database")
        # List of rack rows used by the infrastructure
        self.rack_rows = []
        # List of racks used by the insfrastructure
        self.racks = []

    def _rack_row_dl(self, row) -> ImagePoint:
        # sum height of all previous rows
        pos_y = self.MARGIN_TOP
        for _row in self.rack_rows:
            if _row is row:
                break
            pos_y += (
                int(_row.height * self.SCALE)
                + self.ROW_LABEL_OFFSET
                + self.RACK_LABEL_OFFSET
                + self.RACK_OFFSET
            )
        pos_y += int(row.height * self.SCALE)
        return ImagePoint(self.MARGIN_LEFT, pos_y)

    def _rack_dl(self, row, rack) -> ImagePoint:
        dl = self._rack_row_dl(row)

        # Sum the width of all racks in row before the current rack
        if rack.row.reversed:
            for row_rack in rack.row.racks:
                if row_rack.slot > rack.slot:
                    dl.x += int(row_rack.type.width * self.SCALE) + self.RACK_SPACING
        else:
            for row_rack in rack.row.racks:
                if row_rack.slot < rack.slot:
                    dl.x += int(row_rack.type.width * self.SCALE) + self.RACK_SPACING
        dl.y += self.RACK_LABEL_OFFSET + self.RACK_OFFSET
        return dl

    def _equipment_tl(self, row, rack, equipment) -> ImagePoint:
        tl = self._rack_dl(row, rack)

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

        tl.x += self.RACK_PANE_WIDTH + equipment_width_slot * equipment.type.width * (
            int(equipment.rack.type.width * self.SCALE) - 2 * self.RACK_PANE_WIDTH
        )
        tl.y -= (equipment.type.height + equipment_height_slot) * self.RACK_U_HEIGHT

        return tl

    def _draw_rack_equipment(self, row, rack, equipment):
        logger.debug(
            "Drawing equipment %s in rack %s",
            equipment.name,
            rack.name,
        )

        # top left of equipment
        tl = self._equipment_tl(row, rack, equipment)

        equipment_width = equipment.type.width * (
            int(equipment.rack.type.width * self.SCALE) - 2 * self.RACK_PANE_WIDTH
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

    def _draw_rack(self, row, rack):
        logger.debug("Drawing rack %s (%s)", rack.name, rack.slot)

        # top left of rack
        dl = self._rack_dl(row, rack)

        rack_width = rack.type.width * self.SCALE
        rack_height = rack.type.height * self.SCALE

        # write rack name
        self.ctx.move_to(dl.x, dl.y - rack_height - self.RACK_OFFSET)
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.show_text(f"rack {rack.name}")

        # draw rack frame
        self.ctx.set_source_rgb(0.2, 0.2, 0.2)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            dl.x,
            dl.y - rack_height,
            rack_width,
            rack_height,
        )
        self.ctx.stroke()

        # draw rack panes
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.rectangle(
            dl.x,
            dl.y - rack_height,
            self.RACK_PANE_WIDTH,
            rack_height,
        )
        self.ctx.rectangle(
            dl.x + rack_width - self.RACK_PANE_WIDTH,
            dl.y - rack_height,
            self.RACK_PANE_WIDTH,
            rack_height,
        )
        self.ctx.fill()

        # draw equipments in rack
        for part in self.infrastructure.layout:
            if part.rack is rack:
                for equipment in (
                    list(part.nodes) + list(part.storage) + list(part.network)
                ):
                    self._draw_rack_equipment(row, rack, equipment)

    def _draw_rack_row(self, row):

        logger.debug("Drawing row %s", row.name)

        dl = self._rack_row_dl(row)

        # write row name
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.select_font_face(
            "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )
        self.ctx.set_font_size(14)
        self.ctx.move_to(dl.x, dl.y - int(row.height * self.SCALE))
        self.ctx.show_text(f"row {row.name}")

        # iterate over the racks to draw racks in row
        for rack in self.racks:
            if rack.row is row:
                self._draw_rack(row, rack)

    def _draw_infrastructure(self):
        for row in self.rack_rows:
            self._draw_rack_row(row)

    def draw(self):

        # Get list of racks and rows used by the infrastructure
        for part in self.infrastructure.layout:
            if part.rack not in self.racks:
                self.racks.append(part.rack)
            if part.rack.row not in self.rack_rows:
                self.rack_rows.append(part.rack.row)

        # Sum all rows maximum rack height to calculate image height
        total_row_max_heights = 0
        for rack_row in self.rack_rows:
            row_max_height = 0
            for rack in rack_row.racks:
                row_max_height = max(row_max_height, rack.type.height)
            total_row_max_heights += row_max_height
            # add attributes to row
            rack_row.height = row_max_height

        # Find the maximum rack x to calculate image width
        total_racks_widths = 0
        for rack in self.racks:
            dl = self._rack_dl(rack.row, rack)
            x_tr = dl.x + int(rack.type.width * self.SCALE)
            total_racks_widths = max(total_racks_widths, x_tr)

        surface_width = total_racks_widths + self.MARGIN_LEFT
        surface_height = (
            2 * self.MARGIN_TOP
            + len(self.rack_rows)
            * (self.ROW_LABEL_OFFSET + self.RACK_LABEL_OFFSET + self.RACK_OFFSET)
            + int(total_row_max_heights * self.SCALE)
        )

        self.init_ctx(surface_width, surface_height)
        self._draw_infrastructure()
        self.write()
