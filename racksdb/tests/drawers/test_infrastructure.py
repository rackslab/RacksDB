# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest import mock
import tempfile
from pathlib import Path

from racksdb import RacksDB
from racksdb.drawers.infrastructure import InfrastructureDrawer
from racksdb.drawers.parameters import DrawingParameters
from racksdb.generic.db import DBDictsLoader
from racksdb.errors import RacksDBDrawingError

from ..lib.common import drawing_schema_path, schema_path, db_path


class TestInfrastructureDrawer(unittest.TestCase):
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

    def test_draw_png(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.png"
            drawer = InfrastructureDrawer(
                self.db, "mercury", filename, "png", self.parameters, None, "yaml"
            )
            drawer.draw()
            self.assertTrue(filename.exists())

    def test_draw_svg(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.svg"
            drawer = InfrastructureDrawer(
                self.db, "mercury", filename, "svg", self.parameters, None, "yaml"
            )
            drawer.draw()
            self.assertTrue(filename.exists())

    def test_draw_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.pdf"
            drawer = InfrastructureDrawer(
                self.db, "mercury", filename, "pdf", self.parameters, None, "yaml"
            )
            drawer.draw()
            self.assertTrue(filename.exists())

    def test_draw_not_existing_infrastructure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.png"
            with self.assertRaisesRegex(
                RacksDBDrawingError, "^Unable to find infrastructure fail in database$"
            ):
                InfrastructureDrawer(
                    self.db, "fail", filename, "png", self.parameters, None, "yaml"
                )
            self.assertFalse(filename.exists())

    def test_rack_row_spacing_height(self):
        drawer = InfrastructureDrawer(
            self.db, "mercury", "dontmind.png", "png", self.parameters, None, "yaml"
        )
        # Check that by default, row and racks labels are enabled.
        self.assertTrue(self.parameters.rack.labels)
        self.assertTrue(self.parameters.row.labels)

        # Change values of rack offset and rack label offset to validate sums.
        self.assertEqual(self.parameters.row.label_offset, 20)
        self.parameters.rack.offset = 10
        self.parameters.rack.label_offset = 30

        # Check spacing height between rows with all labels enabled.
        self.assertEqual(drawer._rack_row_spacing_height(), 60)  # 30 + 20 + 10
        # Disable racks labels.
        self.parameters.rack.labels = False
        self.assertEqual(drawer._rack_row_spacing_height(), 30)  # 20 + 10
        # Disable row labels (ie. no labels).
        self.parameters.row.labels = False
        self.assertEqual(drawer._rack_row_spacing_height(), 10)
        # Re-enable racks labels (w/o row labels).
        self.parameters.rack.labels = True
        self.assertEqual(drawer._rack_row_spacing_height(), 40)  # 30 + 10

    def test_labels_call_print_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.png"
            drawer = InfrastructureDrawer(
                self.db, "mercury", filename, "png", self.parameters, None, "yaml"
            )
            # Mock _print_text() method to check if it is called or not.
            drawer._print_text = mock.Mock()

            # Check _print_text() is not called when all labels are disabled.
            (
                self.parameters.rack.labels,
                self.parameters.row.labels,
                self.parameters.infrastructure.equipment_labels,
            ) = (False, False, False)
            drawer.draw()
            drawer._print_text.assert_not_called()
            drawer._print_text.reset_mock()

            # Check _print_text() is called when either rack, row or equipment
            # labels are enabled.
            (
                self.parameters.rack.labels,
                self.parameters.row.labels,
                self.parameters.infrastructure.equipment_labels,
            ) = (True, False, False)
            drawer.draw()
            drawer._print_text.assert_called()
            drawer._print_text.reset_mock()

            (
                self.parameters.rack.labels,
                self.parameters.row.labels,
                self.parameters.infrastructure.equipment_labels,
            ) = (False, True, False)
            drawer.draw()
            drawer._print_text.assert_called()
            drawer._print_text.reset_mock()

            (
                self.parameters.rack.labels,
                self.parameters.row.labels,
                self.parameters.infrastructure.equipment_labels,
            ) = (False, False, True)
            drawer.draw()
            drawer._print_text.assert_called()
            drawer._print_text.reset_mock()
