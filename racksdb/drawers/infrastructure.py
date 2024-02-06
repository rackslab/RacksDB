# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Union
import math
from itertools import chain
import logging

import cairo

from .base import Drawer, ImagePoint
from ..errors import RacksDBError

logger = logging.getLogger(__name__)


class InfrastructureDrawer(Drawer):
    def __init__(self, db, name, file, output_format, parameters):
        super().__init__(db, file, output_format, parameters)
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
        # Calculated at draw time based on dimensions
        self.ratio = 0

    def _rack_row_width(self, rack_row):
        """Return rack row width in mm"""
        total = 0
        for rack in rack_row.racks:
            total += rack.type.width
        return total

    def _rack_row_height(self, rack_row):
        """Return rack row height, ie. the maximum rack height in the row, in mm."""
        row_max_height = 0
        for rack in rack_row.racks:
            row_max_height = max(row_max_height, rack.type.height)
        return row_max_height

    def _rack_width(self, rack) -> Union[float, int]:
        """Return the width of a given rack as a number of pixels. If
        general.pixel_perfect is False, it returns a float value, else it returns the
        integer value rounded below."""
        width = rack.type.width * self.ratio
        if self.parameters.general.pixel_perfect:
            return math.floor(width)
        return width

    def _rack_inside_width(self, rack) -> Union[float, int]:
        """Return the available width inside a given rack as a number of pixels."""
        return self._rack_width(rack) - 2 * self._rack_pane_width

    def _rack_height(self, rack) -> Union[float, int]:
        """Return the height of a given rack as a number of pixels. If
        general.pixel_perfect is False, it returns a float value based on the rack
        height and the computed drawing ratio, else it returns the integer value rounded
        below based on the number of slots in the rack and the unit height."""
        if self.parameters.general.pixel_perfect:
            return rack.type.slots * self._rack_u_height
        else:
            return rack.type.height * self.ratio

    def _equipment_width(self, equipment) -> Union[float, int]:
        """Return the width of a given equipment as a number of pixels. If
        general.pixel_perfect is False, it returns a float value, else it returns the
        integer value rounded below."""
        width = equipment.type.width * self._rack_inside_width(equipment.rack)
        if self.parameters.general.pixel_perfect:
            return math.floor(width)
        return width

    def _equipment_height(self, equipment) -> Union[float, int]:
        """Return the height of a given equipment as a number of pixels."""
        return equipment.type.height * self._rack_u_height

    @property
    def _rack_u_height(self) -> Union[float, int]:
        """Return the height of a rack unit as a number of pixels. If
        general.pixel_perfect is False, it returns a float value, else it returns the
        integer value rounded below."""
        height = self.parameters.rack.u_height * self.ratio
        if self.parameters.general.pixel_perfect:
            return math.floor(height)
        return height

    @property
    def _rack_pane_width(self) -> Union[float, int]:
        """Return the width of rack panes as a number of pixels. If
        general.pixel_perfect is False, it returns a float value, else it returns the
        integer value rounded below."""
        width = self.parameters.rack.pane_width * self.ratio
        if self.parameters.general.pixel_perfect:
            return math.floor(width)
        return width

    def _rack_row_dl(self, row) -> ImagePoint:
        # sum height of all previous rows
        pos_y = self.parameters.margin.top
        for _row in self.rack_rows:
            if _row is row:
                break
            pos_y += (
                int(_row.height * self.ratio)
                + self.parameters.row.label_offset
                + self.parameters.rack.label_offset
                + self.parameters.rack.offset
            )
        pos_y += int(row.height * self.ratio)
        return ImagePoint(self.parameters.margin.left, pos_y)

    def _rack_dl(self, row, rack) -> ImagePoint:
        dl = self._rack_row_dl(row)

        # Sum the width of all racks in row before the current rack
        if rack.row.reversed:
            for row_rack in rack.row.racks:
                if row_rack.slot > rack.slot:
                    dl.x += (
                        int(row_rack.type.width * self.ratio)
                        + self.parameters.rack.spacing
                    )
        else:
            for row_rack in rack.row.racks:
                if row_rack.slot < rack.slot:
                    dl.x += (
                        int(row_rack.type.width * self.ratio)
                        + self.parameters.rack.spacing
                    )
        dl.y += self.parameters.rack.label_offset + self.parameters.rack.offset
        return dl

    def _equipment_width_slot(self, equipment) -> int:
        """Return the slot of the equipment in the rack width."""
        return (equipment.slot - equipment._first.slot) % (1 / equipment.type.width)

    def _equipment_height_slot(self, equipment) -> int:
        """Return the slot of the equipment (ie. rack unit slot) in the rack height."""
        return (
            equipment._first.slot
            - equipment.rack.type.initial
            + math.floor(
                (equipment.slot - equipment._first.slot) * equipment.type.width
            )
            * equipment.type.height
        )

    def _equipment_tl(self, row, rack, equipment) -> ImagePoint:
        tl = self._rack_dl(row, rack)

        equipment_height_slot = self._equipment_height_slot(equipment)
        equipment_width_slot = self._equipment_width_slot(equipment)

        logger.debug(
            "Equipment %s calculated slots → height: %d width: %d",
            equipment.name,
            equipment_height_slot,
            equipment_width_slot,
        )

        tl.x += self._rack_pane_width + equipment_width_slot * self._equipment_width(
            equipment
        )
        if self.parameters.general.pixel_perfect:
            # Center the equipment in the rack by shifting right by half of the
            # difference between width inside the rack and equipment width multiplied by
            # the number of equipment in rack width.
            tl.x += math.floor(
                (
                    self._rack_inside_width(equipment.rack)
                    - self._equipment_width(equipment) / equipment.type.width
                )
                / 2
            )

            # Except for the 1st equipment in rack width, shift other equipment by one
            # pixel on the right so they are all represented the same size despite the
            # equipment frame is drawn inside the equipment surface on its left side.
            if equipment_width_slot > 0:
                tl.x += 1
        tl.y -= (equipment.type.height + equipment_height_slot) * self._rack_u_height

        return tl

    def _draw_equipment_ghost(self, equipment):
        """Draw an equipment as ghosted."""
        logger.debug(
            "Drawing equipment %s in rack %s as ghosted",
            equipment.name,
            equipment.rack.name,
        )

        # Retrieve top-left corner and dimensions of equipment
        tl = self._equipment_tl(equipment.rack.row, equipment.rack, equipment)
        equipment_width = self._equipment_width(equipment)
        equipment_height = self._equipment_height(equipment)

        # draw equipment ghosted background
        colorset = self._find_equipment_colorset(equipment)
        self.ctx.set_source_rgb(*colorset.ghost)
        self.ctx.rectangle(
            tl.x,
            tl.y,
            equipment_width,
            equipment_height,
        )
        self.ctx.fill()

    def _draw_rack_equipment(self, row, rack, equipment):

        # If equipment_tags drawing parameters is set, check the equipment has at least
        # one matching associated tag.
        if self.parameters.infrastructure.equipment_tags is not None and not any(
            equipment_tag in self.parameters.infrastructure.equipment_tags
            for equipment_tag in equipment.tags
        ):
            # If ghost_unselected is true, represent this equipment ghosted.
            if self.parameters.infrastructure.ghost_unselected:
                self._draw_equipment_ghost(equipment)
            # Then skip
            return

        logger.debug(
            "Drawing equipment %s in rack %s",
            equipment.name,
            rack.name,
        )

        # top left of equipment
        tl = self._equipment_tl(row, rack, equipment)

        equipment_width = self._equipment_width(equipment)
        equipment_height = self._equipment_height(equipment)
        width_slot = self._equipment_width_slot(equipment)

        colorset = self._find_equipment_colorset(equipment)

        # Draw chassis in full rack width, only for the equipment on the left side of
        # the rack slot.
        if width_slot == 0:
            self.ctx.set_source_rgb(*colorset.chassis)
            rack_dl = self._rack_dl(row, rack)
            # At the top of the rack, do not cover the rack frame
            if tl.y == rack_dl.y - self._rack_height(rack):
                chassis_top = rack_dl.y - self._rack_height(rack)
            else:
                chassis_top = tl.y

            self.ctx.rectangle(
                rack_dl.x + self._rack_pane_width,
                chassis_top,
                self._rack_inside_width(equipment.rack),
                equipment_height,
            )
            self.ctx.fill()

        # draw equipment background
        self.ctx.set_source_rgb(*colorset.background)
        self.ctx.rectangle(
            tl.x,
            tl.y,
            equipment_width,
            equipment_height,
        )
        self.ctx.fill()

        # draw equipment frame
        self.ctx.set_source_rgb(*colorset.border)
        self.ctx.set_line_width(1)
        # For the equipment on the left side of the rack slot, draw the equipment frame
        # inside the equipment surface on its left side. Else, draw the frame outside
        # the equipment surface.
        if width_slot == 0:
            frame_x = tl.x + 0.5
        else:
            frame_x = tl.x - 0.5
        frame_y = tl.y - 0.5
        # For full-width equipment, draw the frame inside the equipment surface on its
        # right side as well.
        if equipment_width == self._rack_inside_width(rack):
            frame_width = equipment_width - 1
        else:
            frame_width = equipment_width
        self.ctx.rectangle(
            frame_x,
            frame_y,
            frame_width,
            equipment_height,
        )
        self.ctx.stroke()

        self._label_equipment(row, rack, equipment)

    def _label_equipment(self, row, rack, equipment):
        """Label equipment with its name."""

        # Skip if equipment_label drawing parameter is disabled
        if not self.parameters.infrastructure.equipment_labels:
            return

        # Retrieve top-left corner and dimensions of equipment
        tl = self._equipment_tl(row, rack, equipment)
        equipment_width = self._equipment_width(equipment)
        equipment_height = self._equipment_height(equipment)

        # Write equipment name, rotate the text if height > width
        if equipment_height > equipment_width:
            self.ctx.move_to(tl.x, tl.y + 1)
            self.ctx.save()
            self.ctx.rotate(math.pi / 2)
            self._print_text(
                equipment.name, equipment_height, equipment_width, shift_y=True
            )
        else:
            self.ctx.move_to(tl.x, tl.y)
            self._print_text(equipment.name, equipment_width, equipment_height)

        if equipment_height > equipment_width:
            self.ctx.restore()

    def _draw_rack(self, row, rack):
        logger.debug("Drawing rack %s (%s)", rack.name, rack.slot)

        # bottom left of rack
        dl = self._rack_dl(row, rack)
        rack_width = self._rack_width(rack)
        rack_height = self._rack_height(rack)

        # write rack name
        self.ctx.move_to(dl.x, dl.y - rack_height - self.parameters.rack.offset)
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self._print_text(f"rack {rack.name}")

        colorset = self._find_rack_colorset(rack)

        # draw rack frame
        self.ctx.set_source_rgb(*colorset.frame)
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            dl.x - 0.5,
            dl.y - rack_height - 0.5,
            rack_width + 1,
            rack_height,
        )
        self.ctx.stroke()

        # draw rack panes
        self.ctx.set_source_rgb(*colorset.pane)
        self.ctx.rectangle(
            dl.x,
            dl.y - rack_height,
            self._rack_pane_width,
            rack_height - 1,
        )
        self.ctx.rectangle(
            dl.x + rack_width - self._rack_pane_width,
            dl.y - rack_height,
            self._rack_pane_width,
            rack_height - 1,
        )
        self.ctx.fill()

        # draw equipments in rack
        for part in self.infrastructure.layout:
            if part.rack is rack:
                for equipment in chain(
                    part.nodes, part.storage, part.network, part.misc
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
        self.ctx.move_to(dl.x, dl.y - int(row.height * self.ratio))
        self._print_text(f"row {row.name}")

        # iterate over the racks to draw racks in row
        for rack in self.racks:
            if rack.row is row:
                self._draw_rack(row, rack)

    def _draw_infrastructure(self):
        for row in self.rack_rows:
            self._draw_rack_row(row)

    def draw(self):

        logger.debug(
            "Maximum dimensions: %d %d",
            self.parameters.dimensions.width,
            self.parameters.dimensions.height,
        )

        # Get list of racks and rows used by the infrastructure
        for part in self.infrastructure.layout:
            if part.rack not in self.racks:
                self.racks.append(part.rack)
            if part.rack.row not in self.rack_rows:
                self.rack_rows.append(part.rack.row)

        # Search maximum racks row width and sum all rows maximum rack height in mm
        max_row_width = 0
        max_row_racks = 0
        total_row_max_heights = 0
        for rack_row in self.rack_rows:
            max_row_width = max(max_row_width, self._rack_row_width(rack_row))
            max_row_racks = max(max_row_racks, len(rack_row.racks))
            # add height attribute to row
            rack_row.height = self._rack_row_height(rack_row)
            total_row_max_heights += rack_row.height

        logger.debug(
            "total row heights: %d max row width: %d",
            total_row_max_heights,
            max_row_width,
        )

        # Compute total white spaces in width and height
        width_whitespace = (
            self.parameters.margin.left * 2
            + self.parameters.rack.spacing * (max_row_racks - 1)
        )
        height_whitespace = 2 * self.parameters.margin.top + len(self.rack_rows) * (
            self.parameters.row.label_offset
            + self.parameters.rack.label_offset
            + self.parameters.rack.offset
        )

        # Deduce available space to draw in width and height
        available_width = self.parameters.dimensions.width - width_whitespace
        available_height = self.parameters.dimensions.height - height_whitespace
        logger.debug(
            "available draw area in pixels heights: %d width: %d",
            available_height,
            available_width,
        )

        # Compute final ratio
        self.ratio = min(
            available_width / max_row_width, available_height / total_row_max_heights
        )
        logger.debug("Final ratio is: %f", self.ratio)

        # Compute final surface width and height
        surface_width = int(self.ratio * max_row_width + width_whitespace)
        surface_height = int(self.ratio * total_row_max_heights + height_whitespace)

        logger.debug("Final width: %d", surface_width)
        logger.debug("Final height: %d", surface_height)

        self.init_ctx(surface_width, surface_height)
        self._draw_infrastructure()
        self.write()
