# Copyright (c) 2026 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import unittest
from unittest import mock
import tempfile
from pathlib import Path

from racksdb import RacksDB
from racksdb.drawers.collisions import polygons_overlap
from racksdb.drawers.room import RoomDrawer
from racksdb.drawers.parameters import DrawingParameters
from racksdb.generic.db import DBDictsLoader
from racksdb.errors import RacksDBDrawingError

from ..lib.common import drawing_schema_path, schema_path, db_path


def square(x, y, size=1):
    return [(x, y), (x + size, y), (x + size, y + size), (x, y + size)]


class TestPolygonsOverlap(unittest.TestCase):
    def test_overlap(self):
        self.assertTrue(polygons_overlap(square(0, 0, 2), square(1, 1, 2)))

    def test_included(self):
        self.assertTrue(polygons_overlap(square(0, 0, 4), square(1, 1)))

    def test_disjoint(self):
        self.assertFalse(polygons_overlap(square(0, 0), square(5, 5)))

    def test_edge_touching(self):
        self.assertFalse(polygons_overlap(square(0, 0), square(1, 0)))
        self.assertFalse(polygons_overlap(square(0, 0), square(0, 1)))

    def test_corner_touching(self):
        self.assertFalse(polygons_overlap(square(0, 0), square(1, 1)))

    def test_rotated(self):
        # Diamond centered on (2, 0.5) with half-diagonal 1
        diamond = [(1, 0.5), (2, -0.5), (3, 0.5), (2, 1.5)]
        # Bounding boxes overlap but polygons are separated on diamond axes.
        self.assertFalse(polygons_overlap(square(-0.6, 1.4), diamond))
        # Polygons overlap.
        self.assertTrue(polygons_overlap(square(0.5, 0), diamond))


class TestRoomDrawer(unittest.TestCase):
    def setUp(self):
        try:
            self.drawings_schema_path = drawing_schema_path()
            self.schema_path = schema_path()
            self.db_path = db_path()
        except FileNotFoundError as err:
            self.skipTest(err)
        self.parameters = DrawingParameters.load(
            DBDictsLoader({}), self.drawings_schema_path
        )
        self.db = RacksDB.load(schema=self.schema_path, db=self.db_path)

    def _drawer(self, filename="dontmind.png", output_format="png"):
        return RoomDrawer(
            self.db, "noisy", filename, output_format, self.parameters, None, "yaml"
        )

    def _row(self, drawer, name):
        for row in drawer.room.rows:
            if row.name == name:
                return row
        raise KeyError(name)

    def test_draw_formats(self):
        for output_format in ["png", "svg", "pdf"]:
            with self.subTest(output_format=output_format):
                with tempfile.TemporaryDirectory() as tmpdir:
                    filename = Path(tmpdir) / f"output.{output_format}"
                    self._drawer(filename, output_format).draw()
                    self.assertTrue(filename.exists())

    def test_draw_not_existing_room(self):
        with self.assertRaisesRegex(
            RacksDBDrawingError, "^Unable to find room fail in database$"
        ):
            RoomDrawer(
                self.db, "fail", "dontmind.png", "png", self.parameters, None, "yaml"
            )

    def test_no_collision(self):
        drawer = self._drawer()
        # Mock logger to check no warning is emitted, unittest assertNoLogs() is not
        # available in Python < 3.10.
        with mock.patch("racksdb.drawers.room.logger") as logger:
            drawer._check_collisions()
        logger.warning.assert_not_called()
        self.assertEqual(drawer._colliding_racks, set())

    def test_collision(self):
        drawer = self._drawer()
        # Move row R2 at the same position as row R1, racks in both rows must
        # collide.
        self._row(drawer, "R2").position.depth = self._row(drawer, "R1").position.depth
        with self.assertLogs("racksdb.drawers.room", "WARNING") as cm:
            drawer._check_collisions()
        self.assertIn(
            "WARNING:racksdb.drawers.room:Collision detected in room noisy between "
            "racks R1-A01 and R2-A01",
            cm.output,
        )
        self.assertIn("R1-A01", drawer._colliding_racks)
        self.assertIn("R2-A01", drawer._colliding_racks)
        self.assertFalse(any(name.startswith("R3") for name in drawer._colliding_racks))

    def test_rotated_row_edge_touching(self):
        drawer = self._drawer()
        # Rotate row R1 by 90° around its top-left corner, its racks then just
        # touch the left edge of rows R2 and R3 below. This must not be
        # considered as a collision despite trigonometric rounding errors.
        self._row(drawer, "R1").position.rotation = 90
        with mock.patch("racksdb.drawers.room.logger") as logger:
            drawer._check_collisions()
        logger.warning.assert_not_called()
        self.assertEqual(drawer._colliding_racks, set())

    def test_collision_rotated_row(self):
        drawer = self._drawer()
        # Rotate row R1 by 90° and shift it right so that it crosses row R2
        # below. Row R3 racks start at slot 2, after shifted row R1, so they do
        # not collide.
        row = self._row(drawer, "R1")
        row.position.rotation = 90
        row.position.width += 1000
        with self.assertLogs("racksdb.drawers.room", "WARNING"):
            drawer._check_collisions()
        self.assertTrue(any(name.startswith("R2") for name in drawer._colliding_racks))
        self.assertFalse(any(name.startswith("R3") for name in drawer._colliding_racks))

    def test_draw_with_collision(self):
        drawer = self._drawer()
        self._row(drawer, "R2").position.depth = self._row(drawer, "R1").position.depth
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.png"
            drawer.file = filename
            with self.assertLogs("racksdb.drawers.room", "WARNING"):
                drawer.draw()
            self.assertTrue(filename.exists())
