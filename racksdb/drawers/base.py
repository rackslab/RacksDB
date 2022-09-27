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
import logging

logger = logging.getLogger(__name__)


class ImagePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Drawer:
    def __init__(self, db, name, output_format):
        self.db = db
        self.output_format = output_format
        self.surface = None
        self.ctx = None
        self.filename = f"{name}.{output_format}"

    def init_ctx(self, width, height):
        if self.output_format == 'png':
            self.surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, width, height
            )
        elif self.output_format == 'svg':
            self.surface = cairo.SVGSurface(self.filename, width, height)
        elif self.output_format == 'pdf':
            self.surface = cairo.PDFSurface(self.filename, width, height)
        self.ctx = cairo.Context(self.surface)

    def write(self):
        if self.output_format == 'png':
            self.surface.write_to_png(self.filename)
        elif self.output_format in ['svg', 'pdf']:
            self.surface.finish()
            self.surface.flush()
        logger.info("Generated %s", self.filename)
