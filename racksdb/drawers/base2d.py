# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from typing import Union
import logging

import cairo
import gi

from .base import Drawer
from .coordinates import CoordinateDumperFactory
from ..errors import RacksDBDrawingError

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")

# This import is not at the top of the file because gi requires the version to be
# specified with the calls above before importing the modules from repository, thus the
# ruff QA exception on E402.
from gi.repository import Pango, PangoCairo  # noqa: E402


logger = logging.getLogger(__name__)


class ImagePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Drawer2D(Drawer):
    """Base class of drawers of 2D images with cairo, with optional coordinates of
    represented entities in images."""

    def __init__(
        self, db, file, output_format, parameters, coordinates_fh, coordinates_format
    ):
        super().__init__(db, file, output_format, parameters)
        self.coordinates_fh = coordinates_fh
        self.coordinates_format = coordinates_format
        self.coordinates = {}
        self.surface = None
        self.ctx = None

    def init_ctx(self, width, height):
        if self.output_format == "png":
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        elif self.output_format == "svg":
            self.surface = cairo.SVGSurface(self.file, width, height)
        elif self.output_format == "pdf":
            self.surface = cairo.PDFSurface(self.file, width, height)
        else:
            raise RacksDBDrawingError(f"Unsupported image format {self.output_format}")
        self.ctx = cairo.Context(self.surface)

    def write(self):
        if self.output_format == "png":
            self.surface.write_to_png(self.file)
        elif self.output_format in ["svg", "pdf"]:
            self.surface.finish()
            self.surface.flush()
        if self.coordinates_fh is not None:
            self.coordinates_fh.write(
                CoordinateDumperFactory.create(self.coordinates_format).dump(
                    self.coordinates
                )
            )

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
