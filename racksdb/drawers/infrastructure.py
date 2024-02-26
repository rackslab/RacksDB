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


class EquipmentCoordinate:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def _serialized(self):
        return [self.x, self.y, self.width, self.height]


class InfrastructureDrawer(Drawer):
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
            db, file, output_format, parameters, coordinates_fh, coordinates_format
        )
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

    def _rack_in_infrastructure(self, rack) -> bool:
        """Return True if rack is used in infrastructure, False otherwise."""
        for part in self.infrastructure.layout:
            if part.rack.name == rack.name:
                return True

        return False

    def _part_contains_selected_equipment(self, part) -> bool:
        """Return True if the infrastructure part contains equipment that is selected
        for representation in the diagram, False otherwise."""

        # If equipment_tags is unset, all equipment is represented, then it is True.
        if not hasattr(self.parameters.infrastructure, "equipment_tags"):
            return True
        # Iterate over all equipment to check if at least one has matching tag.
        for equipment in chain(part.nodes, part.storage, part.network, part.misc):
            if any(
                equipment_tag in self.parameters.infrastructure.equipment_tags
                for equipment_tag in equipment.tags
            ):
                return True
        # No matching equipment found, return False.
        return False

    def _rack_contains_selected_equipment(self, rack) -> bool:
        """Return True if the given rack contains equipment that is selected
        for representation in the diagram, False otherwise."""
        for part in self.infrastructure.layout:
            if part.rack.name == rack.name:
                if self._part_contains_selected_equipment(part):
                    return True
        return False

    def _rack_must_be_represented(self, rack) -> bool:
        """Return true if the given rack must be represented in infrastructure diagram.
        This method must be called only with racks in rows where the infrastructure is
        present."""
        # When other_racks is true, the rack must be represented as soon as it is in the
        # row.
        if self.parameters.infrastructure.other_racks:
            return True
        # Else the rack must be represented if it used in infrastructure and if it
        # contains selected equipment or discard_empty_rack is disabled.
        return self._rack_in_infrastructure(rack) and (
            not self.parameters.infrastructure.discard_empty_racks
            or self._rack_contains_selected_equipment(rack)
        )

    def _rack_row_width(self, row) -> int:
        """Return rack row width in mm"""
        total = 0

        if row.reversed:
            # If row is reversed, search for the minimum slot among racks to represent
            # in the row.
            min_slot = math.inf
            for rack in row.racks:
                if self._rack_must_be_represented(rack) and rack.slot < min_slot:
                    min_slot = rack.slot
            # Sum widths of all racks over this minimum slot
            for rack in row.racks:
                if rack.slot >= min_slot:
                    total += rack.type.width

        else:
            max_slot = 0
            # Else, search for the maximum slot among racks to represent in the row.
            for rack in row.racks:
                if self._rack_must_be_represented(rack) and rack.slot > max_slot:
                    max_slot = rack.slot
            # Sum widths of all racks below this maximum slot
            for rack in row.racks:
                if rack.slot <= max_slot:
                    total += rack.type.width

        return total

    def _rack_row_height(self, row) -> int:
        """Return rack row height, ie. the maximum rack height among the represented
        racks in the row, in mm."""
        row_max_height = 0
        for rack in row.racks:
            if self._rack_must_be_represented(rack):
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

    def _rack_dl(self, rack) -> ImagePoint:
        dl = self._rack_row_dl(rack.row)

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

    def _equipment_tl(self, equipment) -> ImagePoint:
        tl = self._rack_dl(equipment.rack)

        logger.debug(
            "Equipment %s calculated slots → height: %d width: %d",
            equipment.name,
            equipment.position.height,
            equipment.position.width,
        )

        tl.x += (
            self._rack_pane_width
            + equipment.position.width * self._equipment_width(equipment)
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
            if equipment.position.width > 0:
                tl.x += 1
        tl.y -= (
            equipment.type.height + equipment.position.height
        ) * self._rack_u_height

        return tl

    def _draw_equipment_ghost(self, equipment):
        """Draw an equipment as ghosted."""
        logger.debug(
            "Drawing equipment %s in rack %s as ghosted",
            equipment.name,
            equipment.rack.name,
        )

        # Retrieve top-left corner and dimensions of equipment
        tl = self._equipment_tl(equipment)
        equipment_width = self._equipment_width(equipment)
        equipment_height = self._equipment_height(equipment)

        # draw equipment ghosted background
        colorset = self._find_equipment_colorset(equipment)
        self.ctx.set_source_rgba(*colorset.ghost)
        self.ctx.rectangle(
            tl.x,
            tl.y,
            equipment_width,
            equipment_height,
        )
        self.ctx.fill()

    def _draw_rack_equipment(self, equipment):

        # If equipment_tags drawing parameters is set, check the equipment has at least
        # one matching associated tag.
        if hasattr(self.parameters.infrastructure, "equipment_tags") and not any(
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
            equipment.rack.name,
        )

        # top left of equipment
        tl = self._equipment_tl(equipment)

        equipment_width = self._equipment_width(equipment)
        equipment_height = self._equipment_height(equipment)

        colorset = self._find_equipment_colorset(equipment)

        # Draw chassis in full rack width, only for the equipment on the left side of
        # the rack slot.
        if equipment.position.width == 0:
            self.ctx.set_source_rgba(*colorset.chassis)
            rack_dl = self._rack_dl(equipment.rack)
            # At the top of the rack, do not cover the rack frame
            if tl.y == rack_dl.y - self._rack_height(equipment.rack):
                chassis_top = rack_dl.y - self._rack_height(equipment.rack)
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
        self.ctx.set_source_rgba(*colorset.background)
        self.ctx.rectangle(
            tl.x,
            tl.y,
            equipment_width,
            equipment_height,
        )
        self.ctx.fill()

        self.coordinates[equipment.name] = EquipmentCoordinate(
            tl.x,
            tl.y,
            equipment_width,
            equipment_height,
        )

        # draw equipment frame
        self.ctx.set_source_rgba(*colorset.border)
        self.ctx.set_line_width(1)
        # For the equipment on the left side of the rack slot, draw the equipment frame
        # inside the equipment surface on its left side. Else, draw the frame outside
        # the equipment surface.
        if equipment.position.width == 0:
            frame_x = tl.x + 0.5
        else:
            frame_x = tl.x - 0.5
        frame_y = tl.y - 0.5
        # For full-width equipment, draw the frame inside the equipment surface on its
        # right side as well.
        if equipment_width == self._rack_inside_width(equipment.rack):
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

        self._label_equipment(equipment)

    def _label_equipment(self, equipment):
        """Label equipment with its name."""

        # Skip if equipment_label drawing parameter is disabled
        if not self.parameters.infrastructure.equipment_labels:
            return

        # Retrieve top-left corner and dimensions of equipment
        tl = self._equipment_tl(equipment)
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

    def _draw_rack(self, rack):
        logger.debug("Drawing rack %s (%s)", rack.name, rack.slot)

        # bottom left of rack
        dl = self._rack_dl(rack)
        rack_width = self._rack_width(rack)
        rack_height = self._rack_height(rack)

        # write rack name
        self.ctx.move_to(dl.x, dl.y - rack_height - self.parameters.rack.offset)
        self.ctx.set_source_rgba(0, 0, 0, 1)  # black
        self._print_text(f"rack {rack.name}", max_width=self._rack_width(rack))

        colorset = self._find_rack_colorset(rack)

        # draw rack frame
        self.ctx.set_source_rgba(*colorset.frame)
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            dl.x - 0.5,
            dl.y - rack_height - 0.5,
            rack_width + 1,
            rack_height,
        )
        self.ctx.stroke()

        # draw rack panes
        self.ctx.set_source_rgba(*colorset.pane)
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

        # Rack is not in the infrastructure, it is represented because other_racks is
        # enabled. In this case, fill the rack with the frame color to imitate a closed
        # door.
        if not self._rack_in_infrastructure(rack):
            self.ctx.set_source_rgba(*colorset.frame)
            self.ctx.rectangle(
                dl.x + self._rack_pane_width,
                dl.y - rack_height,
                self._rack_inside_width(rack),
                rack_height - 1,
            )
            self.ctx.fill()
            # Lease now to avoid equipment drawing loop.
            return

        # draw equipments in rack
        for part in self.infrastructure.layout:
            if part.rack.name == rack.name:
                for equipment in chain(
                    part.nodes, part.storage, part.network, part.misc
                ):
                    self._draw_rack_equipment(equipment)

    def _draw_rack_row(self, row):

        logger.debug("Drawing row %s", row.name)

        dl = self._rack_row_dl(row)

        # write row name
        self.ctx.set_source_rgba(0, 0, 0, 1)  # black
        self.ctx.select_font_face(
            "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )
        self.ctx.set_font_size(14)
        self.ctx.move_to(dl.x, dl.y - int(row.height * self.ratio))
        self._print_text(f"row {row.name}")

        # iterate over the racks to draw racks in row
        for rack in self.racks:
            if rack.row is row:
                self._draw_rack(rack)

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
            # If discard_empty_racks is True, skip parts without equipment selected for
            # representation in the diagram.
            if (
                self.parameters.infrastructure.discard_empty_racks
                and not self._part_contains_selected_equipment(part)
            ):
                continue
            # If other_racks is True, select all racks in part rack row.
            if self.parameters.infrastructure.other_racks:
                for rack in part.rack.row.racks:
                    if rack not in self.racks:
                        self.racks.append(rack)
            # Else select all racks in part.
            elif part.rack not in self.racks:
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
