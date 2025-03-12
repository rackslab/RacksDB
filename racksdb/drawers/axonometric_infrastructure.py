# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Union
import math
from itertools import chain
import logging

import cairo

from .base import ImagePoint
from .infrastructure import InfrastructureDrawer, EquipmentCoordinate
from ..errors import RacksDBDrawingError

logger = logging.getLogger(__name__)


class AxonometricInfrastructureDrawer(InfrastructureDrawer):

    @property
    def x_cos(self):
        return math.cos(math.radians(self.parameters.axonometric.angles.x))

    @property
    def x_sin(self):
        return math.sin(math.radians(self.parameters.axonometric.angles.x))

    @property
    def z_cos(self):
        return math.cos(math.radians(self.parameters.axonometric.angles.z))

    @property
    def z_sin(self):
        return math.sin(math.radians(self.parameters.axonometric.angles.z))

    def _rack_depth(self, rack) -> Union[float, int]:
        """Return the depth of a given rack as a number of pixels. If
        general.pixel_perfect is False, it returns a float value, else it returns the
        integer value rounded below."""
        depth = rack.type.depth * self.ratio
        if self.parameters.general.pixel_perfect:
            return math.floor(depth)
        return depth

    def _rack_row_depth(self, row) -> int:
        """Return rack row depth, ie. the maximum rack depth among the represented
        racks in the row, in mm."""
        row_max_depth = 0
        for rack in row.racks:
            if self._rack_must_be_represented(rack):
                row_max_depth = max(row_max_depth, rack.type.depth)
        return row_max_depth

    def _nb_represented_racks_in_row(self, row) -> int:
        """Return the number of represented racks in a given row."""
        nb = 0
        for rack in row.racks:
            if self._rack_must_be_represented(rack):
                nb += 1
        return nb

    def _rack_row_dl_abs(self, row) -> ImagePoint:
        point = ImagePoint(self._rack_row_depth(row) * self.x_cos, 0)
        # sum height of all previous rows
        for index, rack_row in enumerate(self.rack_rows):
            # Add width of first row
            point.y += (
                self._rack_row_height(rack_row)
                + self._rack_row_depth(rack_row) * self.x_sin
            )
            # Add first row width
            if index == 0:
                point.y += self._rack_row_width(rack_row) * self.z_sin
            else:
                point.y += self._rack_row_depth(rack_row) * self.z_sin
            if rack_row is row:
                break
        return point

    def _rack_row_dl(self, row) -> ImagePoint:
        point = self._rack_row_dl_abs(row)
        point.x *= self.ratio
        point.y *= self.ratio

        point.x += self.parameters.margin.left
        point.y += self.parameters.margin.top
        point.y += self._vertical_spacing_above_first_row()

        # Count number of represented racks in this row to define the rack spacing in
        # height.
        nb_height_spacing = self._nb_represented_racks_in_row(self.top_rack.row) - 1
        point.y += self.parameters.rack.spacing * nb_height_spacing * self.z_sin

        # sum height of all previous rows
        for _row in self.rack_rows:
            if _row is row:
                break
            point.y += self._rack_row_spacing_height()
        return point

    def _rack_dl_abs(self, rack) -> ImagePoint:
        point = self._rack_row_dl_abs(rack.row)
        x_offset = 0
        # Sum the width of all racks in row before the current rack
        if rack.row.reversed:
            for row_rack in rack.row.racks:
                if row_rack.slot > rack.slot:
                    x_offset += row_rack.type.width
        else:
            for row_rack in rack.row.racks:
                if row_rack.slot < rack.slot:
                    x_offset += row_rack.type.width
        point.x += x_offset * self.z_cos
        point.y -= x_offset * self.z_sin
        return point

    def _rack_dl(self, rack) -> ImagePoint:
        dl = self._rack_dl_abs(rack)
        dl.x *= self.ratio
        dl.y *= self.ratio

        dl.x += self.parameters.margin.left
        dl.y += self.parameters.margin.top
        dl.y += self._vertical_spacing_above_first_row()

        # Count number of represented racks in this row to define the rack spacing in
        # height.
        nb_height_spacing = self._nb_represented_racks_in_row(self.top_rack.row) - 1
        dl.y += self.parameters.rack.spacing * nb_height_spacing * self.z_sin

        for _row in self.rack_rows:
            if _row is rack.row:
                break
            dl.y += self._rack_row_spacing_height()

        # Add x spacing between all racks in row before the current rack
        x_offset = 0
        if rack.row.reversed:
            for row_rack in rack.row.racks:
                if (
                    self._rack_must_be_represented(row_rack)
                    and row_rack.slot > rack.slot
                ):
                    x_offset += self.parameters.rack.spacing
        else:
            for row_rack in rack.row.racks:
                if (
                    self._rack_must_be_represented(row_rack)
                    and row_rack.slot < rack.slot
                ):
                    x_offset += self.parameters.rack.spacing
        dl.x += x_offset * self.z_cos
        dl.y -= x_offset * self.z_sin
        return dl

    def _equipment_tl(self, equipment) -> ImagePoint:
        tl = self._rack_dl(equipment.rack)

        logger.debug(
            "Equipment %s calculated slots → height: %d width: %d",
            equipment.name,
            equipment.position.height,
            equipment.position.width,
        )

        x_offset = (
            self._rack_pane_width
            + equipment.position.width * self._equipment_width(equipment)
        )

        tl.x += x_offset * self.z_cos
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
        ) * self._rack_u_height + x_offset * self.z_sin

        return tl

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

        # draw equipment background
        self.ctx.set_source_rgba(*colorset.background)
        self.ctx.move_to(tl.x, tl.y)
        self.ctx.rel_line_to(
            equipment_width * self.z_cos, -equipment_width * self.z_sin
        )
        self.ctx.rel_line_to(0, equipment_height)
        self.ctx.rel_line_to(
            -equipment_width * self.z_cos, equipment_width * self.z_sin
        )
        self.ctx.line_to(tl.x, tl.y)
        self.ctx.fill()

        # draw equipment top

        # FIXME: support equipment depth?
        rack_depth = self._rack_depth(equipment.rack)
        self.ctx.set_source_rgba(*colorset.top_side)
        self.ctx.move_to(tl.x, tl.y)
        self.ctx.rel_line_to(
            equipment_width * self.z_cos, -equipment_width * self.z_sin
        )
        self.ctx.rel_line_to(-rack_depth * self.x_cos, -rack_depth * self.x_sin)
        self.ctx.rel_line_to(
            -equipment_width * self.z_cos, equipment_width * self.z_sin
        )
        self.ctx.line_to(tl.x, tl.y)
        self.ctx.fill()

        # draw equipment left side
        self.ctx.set_source_rgba(*colorset.left_side)
        self.ctx.move_to(tl.x, tl.y)
        self.ctx.rel_line_to(0, equipment_height)
        self.ctx.rel_line_to(-rack_depth * self.x_cos, -rack_depth * self.x_sin)
        self.ctx.rel_line_to(0, -equipment_height)
        self.ctx.line_to(tl.x, tl.y)
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

        self.ctx.move_to(frame_x, frame_y)
        self.ctx.rel_line_to(frame_width * self.z_cos, -frame_width * self.z_sin)
        self.ctx.rel_line_to(0, equipment_height)
        self.ctx.rel_line_to(-frame_width * self.z_cos, frame_width * self.z_sin)
        self.ctx.line_to(frame_x, frame_y)
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

        self.ctx.save()
        self.ctx.move_to(tl.x, tl.y)
        self.ctx.set_matrix(cairo.Matrix(yx=-self.z_sin, xx=self.z_cos))
        # Write equipment name, rotate the text if height > width
        if equipment_height > equipment_width:
            self.ctx.rel_move_to(0, 1)
            self.ctx.rotate(math.pi / 2)
            self._print_text(
                equipment.name, equipment_height, equipment_width, shift_y=True
            )
        else:
            self._print_text(equipment.name, equipment_width, equipment_height)
        self.ctx.restore()

    def _draw_rack(self, rack):
        logger.debug("Drawing rack %s (%s)", rack.name, rack.slot)

        # bottom left of rack
        dl = self._rack_dl(rack)
        rack_width = self._rack_width(rack)
        rack_height = self._rack_height(rack)
        rack_depth = self._rack_depth(rack)

        # write rack name if rack labels are enabled
        if self.parameters.rack.labels:
            self.ctx.move_to(
                dl.x - self._rack_row_depth(rack.row) * self.ratio * self.x_cos,
                dl.y
                - rack_height
                - self._rack_row_depth(rack.row) * self.ratio * self.x_sin
                - self.parameters.rack.label_offset,
            )
            self.ctx.save()
            self.ctx.set_matrix(cairo.Matrix(yx=-self.z_sin, xx=self.z_cos))
            self.ctx.set_source_rgba(0, 0, 0, 1)  # black
            self._print_text(f"rack {rack.name}", max_width=self._rack_width(rack))
            self.ctx.restore()

        colorset = self._find_rack_colorset(rack)

        # coordinates of racks bottom
        bfl = ImagePoint(dl.x - 0.5, dl.y - 0.5)
        bfr = ImagePoint(
            bfl.x + rack_width * self.z_cos, bfl.y - rack_width * self.z_sin
        )
        bbr = ImagePoint(
            bfr.x - rack_depth * self.x_cos, bfr.y - rack_depth * self.x_sin
        )
        bbl = ImagePoint(
            bbr.x - rack_width * self.z_cos, bbr.y + rack_width * self.z_sin
        )

        # draw rack bottom
        self.ctx.set_source_rgba(*colorset.bottom_side)
        self.ctx.move_to(bfl.x, bfl.y)
        self.ctx.line_to(bfr.x, bfr.y)
        self.ctx.line_to(bbr.x, bbr.y)
        self.ctx.line_to(bbl.x, bbl.y)
        self.ctx.line_to(bfl.x, bfl.y)
        self.ctx.fill()

        # draw rack right side
        self.ctx.set_source_rgba(*colorset.right_side)
        self.ctx.move_to(bfr.x, bfr.y)
        self.ctx.rel_line_to(0, -rack_height)
        self.ctx.rel_line_to(
            -rack_depth * self.x_cos,
            -rack_depth * self.x_sin,
        )
        self.ctx.rel_line_to(0, rack_height)
        self.ctx.line_to(bfr.x, bfr.y)
        self.ctx.fill()

        # draw equipments in rack
        for part in self.infrastructure.layout:
            if part.rack.name == rack.name:
                for equipment in sorted(
                    chain(part.nodes, part.storage, part.network, part.misc),
                    key=lambda equipment: (
                        equipment.position.height,
                        -equipment.position.width,
                    ),
                ):
                    self._draw_rack_equipment(equipment)

        # draw rack front panes
        self.ctx.set_source_rgba(*colorset.pane)
        # left
        self.ctx.move_to(bfl.x, bfl.y)
        self.ctx.rel_line_to(
            self._rack_pane_width * self.z_cos,
            -self._rack_pane_width * self.z_sin,
        )
        self.ctx.rel_line_to(0, -rack_height)
        self.ctx.line_to(bfl.x, bfl.y - rack_height)
        self.ctx.line_to(bfl.x, bfl.y)
        self.ctx.fill()

        # right
        self.ctx.move_to(
            bfr.x - self._rack_pane_width * self.z_cos,
            bfr.y + self._rack_pane_width * self.z_sin,
        )
        self.ctx.line_to(bfr.x, bfr.y)
        self.ctx.rel_line_to(0, -rack_height)
        self.ctx.rel_line_to(
            -self._rack_pane_width * self.z_cos,
            self._rack_pane_width * self.z_sin,
        )
        self.ctx.rel_line_to(0, rack_height)
        self.ctx.fill()

        # draw rack left side
        self.ctx.set_source_rgba(*colorset.left_side)
        self.ctx.move_to(bfl.x, bfl.y)
        self.ctx.rel_line_to(0, -rack_height)
        self.ctx.rel_line_to(
            -rack_depth * self.x_cos,
            -rack_depth * self.x_sin,
        )
        self.ctx.rel_line_to(0, rack_height)
        self.ctx.line_to(bfl.x, bfl.y)
        self.ctx.fill()

        # draw rack top side
        self.ctx.set_source_rgba(*colorset.top_side)
        self.ctx.move_to(bfl.x, bfl.y - rack_height)
        self.ctx.line_to(bfr.x, bfr.y - rack_height)
        self.ctx.line_to(bbr.x, bbr.y - rack_height)
        self.ctx.line_to(bbl.x, bbl.y - rack_height)
        self.ctx.line_to(bfl.x, bfl.y - rack_height)
        self.ctx.fill()

        # Rack is not in the infrastructure, it is represented because other_racks is
        # enabled. In this case, fill the rack with the frame color to imitate a closed
        # door.
        if not self._rack_in_infrastructure(rack):
            self.ctx.set_source_rgba(*colorset.frame)
            self.ctx.move_to(
                bfl.x + self._rack_pane_width * self.z_cos,
                bfl.y - self._rack_pane_width * self.z_sin,
            )
            self.ctx.rel_line_to(
                (rack_width - 2 * self._rack_pane_width) * self.z_cos,
                -(rack_width - 2 * self._rack_pane_width) * self.z_sin,
            )
            self.ctx.rel_line_to(0, -rack_height)
            self.ctx.rel_line_to(
                -(rack_width - 2 * self._rack_pane_width) * self.z_cos,
                +(rack_width - 2 * self._rack_pane_width) * self.z_sin,
            )
            self.ctx.line_to(
                bfl.x + self._rack_pane_width * self.z_cos,
                bfl.y - self._rack_pane_width * self.z_sin,
            )
            self.ctx.fill()
            # Lease now to avoid equipment drawing loop.
            return

    def _draw_rack_row(self, row):

        logger.debug("Drawing row %s", row.name)

        dl = self._rack_row_dl(row)

        # write row name if row labels are enabled
        if self.parameters.row.labels:
            self.ctx.move_to(
                dl.x - self._rack_row_depth(row) * self.ratio * self.x_cos,
                dl.y
                - self._rack_row_height(row) * self.ratio
                - self._rack_row_depth(row) * self.ratio * self.x_sin
                - self._rack_row_labels_height(),
            )

            self.ctx.save()
            self.ctx.set_matrix(cairo.Matrix(yx=-self.z_sin, xx=self.z_cos))
            self.ctx.set_source_rgba(0, 0, 0, 1)  # black
            self.ctx.select_font_face(
                "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
            )
            self.ctx.set_font_size(14)
            self._print_text(f"row {row.name}")
            self.ctx.restore()

        # iterate over the racks to draw racks in row, starting from the end of row.
        for rack in sorted(
            self.racks, key=lambda rack: rack.slot, reverse=not row.reversed
        ):
            if rack.row is row:
                self._draw_rack(rack)

    def draw(self):
        logger.info(
            "Generating axonometric representation of infrastructure %s",
            self.infrastructure.name,
        )

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

        if not self.racks:
            raise RacksDBDrawingError(
                "Unable to find racks to draw with filters provided in drawing "
                "parameters"
            )

        # Search maximum racks row width and sum all rows maximum rack height in mm
        dl = self._rack_dl_abs(self.racks[0])
        max_x = dl.x
        min_y = max_y = dl.y
        self.top_rack = rack_right = self.racks[0]
        for rack in self.racks:
            dl = self._rack_dl_abs(rack)
            if dl.x > max_x:
                max_x = dl.x
                rack_right = rack
            if dl.y < min_y:
                self.top_rack = rack
            max_y = max(max_y, dl.y)

        required_height = max_y
        required_width = max_x + rack_right.type.width * self.z_cos

        logger.debug(
            "required heights: %d required width: %d",
            required_height,
            required_width,
        )

        # Compute total white spaces in width and height

        # Count number of racks in this row to define the rack spacing in width.
        nb_width_spacing = self._nb_represented_racks_in_row(rack_right.row) - 1
        width_whitespace = (
            self.parameters.margin.left * 2
            + self.parameters.rack.spacing * nb_width_spacing * self.z_cos
        )

        # Count number of represented racks in this row to define the rack spacing in
        # height.
        nb_height_spacing = self._nb_represented_racks_in_row(self.top_rack.row) - 1
        height_whitespace = (
            2 * self.parameters.margin.top
            + self._vertical_spacing_above_first_row()
            + (len(self.rack_rows) - 1) * self._rack_row_spacing_height()
            + self.parameters.rack.spacing * nb_height_spacing * self.z_sin
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
            available_width / required_width, available_height / required_height
        )
        logger.debug("Final ratio is: %f", self.ratio)

        # Compute final surface width and height
        surface_width = int(self.ratio * required_width + width_whitespace)
        surface_height = int(self.ratio * required_height + height_whitespace)

        logger.debug("Final width: %d", surface_width)
        logger.debug("Final height: %d", surface_height)

        self.init_ctx(surface_width, surface_height)
        self._draw_infrastructure()
        self.write()
