# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

import cairo

logger = logging.getLogger(__name__)


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
