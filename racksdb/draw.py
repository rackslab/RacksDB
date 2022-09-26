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


import cairo
import math
import logging

from .generic.db import DBExpandableObject
from .errors import RacksDBError

logger = logging.getLogger(__name__)


class InfrastructureDrawer:

    MARGIN_TOP = 30
    ROW_LABEL_OFFSET = 20
    RACK_LABEL_OFFSET = 20
    MARGIN_LEFT = 30
    RACK_U_HEIGHT = 20
    RACK_HEIGHT = RACK_U_HEIGHT * 42
    RACK_ROW_HEIGHT = 500
    RACK_FULL_WIDTH = 200  # including 2 panes
    RACK_PANE_WIDTH = 10
    RACK_WIDTH = RACK_FULL_WIDTH - 2 * RACK_PANE_WIDTH
    RACK_SPACING = 3  # space between racks

    def __init__(self, db, infrastructure_name):
        self.db = db
        self.infrastructure = None
        for infrastructure in self.db.infrastructures:
            if infrastructure.name == infrastructure_name:
                self.infrastructure = infrastructure
        if self.infrastructure is None:
            raise RacksDBError(
                f"Unable to find infrastructure {infrastructure_name} in database"
            )

        WIDTH, HEIGHT = 1024, 1024

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        self.ctx = cairo.Context(self.surface)

    def _draw_rack_node(self, row_index, rack, node, start_slot):
        logger.debug(
            "Drawing node %s in rack %s",
            node.name,
            rack.name,
        )

        node_height_slot = (
            start_slot
            + math.floor((node.slot - start_slot) * node.type.width)
            * node.type.height
        )
        node_width_slot = (node.slot - start_slot) % (1 / node.type.width)

        logger.debug(
            "Node %s calculated slots → height: %d width: %d",
            node.name,
            node_height_slot,
            node_width_slot,
        )

        # top left of node
        x_node = (
            self.MARGIN_LEFT
            + (self.RACK_FULL_WIDTH + self.RACK_SPACING) * rack.slot
            + self.RACK_PANE_WIDTH
            + node_width_slot * node.type.width * self.RACK_WIDTH
        )
        y_node = (
            self.MARGIN_TOP
            + self.ROW_LABEL_OFFSET
            + self.RACK_LABEL_OFFSET
            + self.RACK_ROW_HEIGHT * row_index
            + (41 - node_height_slot) * self.RACK_U_HEIGHT
        )

        node_width = node.type.width * self.RACK_WIDTH
        node_height = node.type.height * self.RACK_U_HEIGHT

        # draw node background
        self.ctx.set_source_rgb(0.6, 0.6, 0.6)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            x_node,
            y_node,
            node_width,
            node_height,
        )
        self.ctx.fill()

        # draw node frame
        self.ctx.set_source_rgb(0.2, 0.2, 0.2)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            x_node,
            y_node,
            node_width,
            node_height,
        )
        self.ctx.stroke()

        # write node name
        self.ctx.move_to(x_node + 3, y_node + 15)
        self.ctx.show_text(node.name)

    def _draw_rack(self, row_index, rack):
        logger.debug("Drawing rack %s (%s)", rack.name, rack.slot)

        # top left of rack
        x_rack = (
            self.MARGIN_LEFT
            + (self.RACK_FULL_WIDTH + self.RACK_SPACING) * rack.slot
        )
        y_rack = (
            self.MARGIN_TOP
            + self.ROW_LABEL_OFFSET
            + self.RACK_ROW_HEIGHT * row_index
        )

        # write rack name
        self.ctx.move_to(x_rack, y_rack)
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.show_text(f"rack {rack.name}")

        # draw rack frame
        self.ctx.set_source_rgb(0.2, 0.2, 0.2)  # grey
        self.ctx.set_line_width(1)
        self.ctx.rectangle(
            x_rack,
            y_rack + self.RACK_LABEL_OFFSET,
            self.RACK_FULL_WIDTH,
            self.RACK_HEIGHT,
        )
        self.ctx.stroke()

        # draw rack panes
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.rectangle(
            x_rack,
            y_rack + self.RACK_LABEL_OFFSET,
            self.RACK_PANE_WIDTH,
            self.RACK_HEIGHT,
        )
        self.ctx.rectangle(
            x_rack + self.RACK_FULL_WIDTH - self.RACK_PANE_WIDTH,
            y_rack + self.RACK_LABEL_OFFSET,
            self.RACK_PANE_WIDTH,
            self.RACK_HEIGHT,
        )
        self.ctx.fill()

        # draw equipments in rack
        for part in self.infrastructure.layout:
            if part.rack is rack:
                for node in part.nodes:
                    if isinstance(node, DBExpandableObject):
                        for _node in node.objects():
                            self._draw_rack_node(
                                row_index, rack, _node, node.slot.start
                            )
                    else:
                        self._draw_rack_node(row_index, rack, node, node.slot)

    def _draw_rack_row(self, index, row, racks):

        logger.debug("Drawing row %s", row.name)
        # write row name
        self.ctx.set_source_rgb(0, 0, 0)  # black
        self.ctx.select_font_face(
            "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )
        self.ctx.set_font_size(14)
        self.ctx.move_to(
            self.MARGIN_LEFT, self.MARGIN_TOP + self.RACK_ROW_HEIGHT * index
        )
        self.ctx.show_text(f"row {row.name}")

        # iterate over the racks to draw racks in row
        for rack in racks:
            if rack.row is row:
                self._draw_rack(index, rack)

    def _draw_infrastructure(self):
        rack_rows = []
        racks = []

        # get list of racks used by the infrastructure
        for part in self.infrastructure.layout:
            if part.rack not in racks:
                racks.append(part.rack)
            if part.rack.row not in rack_rows:
                rack_rows.append(part.rack.row)

        for index, row in enumerate(rack_rows):
            self._draw_rack_row(index, row, racks)

    def draw(self):
        self._draw_infrastructure()
        self.surface.write_to_png(
            f"{self.infrastructure.name}.png"
        )  # Output to PNG
