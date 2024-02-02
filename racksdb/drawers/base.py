# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Union
import logging

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")

# This import is not at the top of the file because gi requires the version to be
# specified with the calls above before importing the modules from repository, thus the
# ruff QA exception on E402.
from gi.repository import Pango, PangoCairo  # noqa: E402


logger = logging.getLogger(__name__)


class DefaultRackColorSet:
    frame = (0.2, 0.2, 0.2)  # aka. #333333 (dark gray)
    pane = (0, 0, 0)  # aka. #000000 (black)


class DefaultEquipmentColorSet:
    background = (0.6, 0.6, 0.6)  # aka. #999999 (light gray)
    border = (0.2, 0.2, 0.2)  # aka. #333333 (dark gray)


class ImagePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Drawer:
    def __init__(self, db, file, output_format, parameters):
        self.db = db
        self.file = file
        self.output_format = output_format
        self.parameters = parameters
        self.surface = None
        self.ctx = None

    def init_ctx(self, width, height):
        if self.output_format == "png":
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        elif self.output_format == "svg":
            self.surface = cairo.SVGSurface(self.file, width, height)
        elif self.output_format == "pdf":
            self.surface = cairo.PDFSurface(self.file, width, height)
        self.ctx = cairo.Context(self.surface)

    def write(self):
        if self.output_format == "png":
            self.surface.write_to_png(self.file)
        elif self.output_format in ["svg", "pdf"]:
            self.surface.finish()
            self.surface.flush()

    def _find_rack_colorset(self, rack):
        """Return the rack matching coloring rule defined in drawing parameters or the
        default rack color set.

        An rack coloring rule can have an rack type name and a list of tags. For a
        coloring rule to match a rack, the following conditions must be verified:

        - If the coloring rule has a type, the id of the rack type must match.
        - If the coloring rule has a list of tags, the rack must have tags and its
          tags must contain all coloring rule tags.

        In other cases, the coloring rule does not match. If no coloring rule matches
        the rack, the default rack color set is returned."""
        for rule in self.parameters.colors.racks:
            if hasattr(rule, "type") and rule.type != rack.type.id:
                continue
            if hasattr(rule, "tags") and (
                not hasattr(rack, "tags")
                or not all(tag in rack.tags for tag in rule.tags)
            ):
                continue
            return rule
        return DefaultRackColorSet

    def _find_equipment_colorset(self, equipment):
        """Return the equipment matching coloring rule defined in drawing parameters or
        the default equipment color set.

        An equipment coloring rule can have an equipment type name and a list of
        tags. For a coloring rule to match an equipment, the following conditions
        must be verified:

        - If the coloring rule has a type, the id of the equipment type must match.
        - If the coloring rule has a list of tags, the equipment must have tags
          and its tags must contain all coloring rule tags.

        In other cases, the coloring rule does not match. If no coloring rule matches
        the equipment, the default equipment color set is returned."""
        for rule in self.parameters.colors.equipments:
            if hasattr(rule, "type") and rule.type != equipment.type.id:
                continue
            if hasattr(rule, "tags") and (
                not hasattr(equipment, "tags")
                or not all(tag in equipment.tags for tag in rule.tags)
            ):
                continue
            return rule
        return DefaultEquipmentColorSet

    def _print_text(
        self,
        text: str,
        max_width: Union[int, None] = None,
        max_height: Union[int, None] = None,
        shift_x: bool = False,
        shift_y: bool = False,
    ) -> None:
        """Print text label in context. The text size can possibly be responsive to
        maximum width and height. The boolean shift_x and shift_y can be set to True in
        order to shift the position of the text label by its height vertically or
        horizontally respectively."""
        layout = PangoCairo.create_layout(self.ctx)
        layout.set_alignment(Pango.Alignment.CENTER)
        # Try multiple decreasing size until it fits into optional max width/height
        for size in range(12, 4, -1):
            layout.set_font_description(
                Pango.font_description_from_string(f"Sans Serif Normal {size}")
            )
            layout.set_markup(text, -1)
            _, extents = layout.get_pixel_extents()
            tw, th = extents.width, extents.height
            # If max_{width/height} is set, text label width/height must be smaller.
            if (max_width is None or tw < max_width) and (
                max_height is None or th < max_height
            ):
                break
        if shift_x:
            self.ctx.rel_move_to(-th, 0)
        if shift_y:
            self.ctx.rel_move_to(0, -th)
        PangoCairo.show_layout(self.ctx, layout)
