# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import unittest
import tempfile
from pathlib import Path

from racksdb import RacksDB
from racksdb.drawers.axonometric_infrastructure import AxonometricInfrastructureDrawer
from racksdb.drawers.parameters import DrawingParameters
from racksdb.generic.db import DBDictsLoader
from racksdb.errors import RacksDBDrawingError

from ..lib.common import drawing_schema_path, schema_path, db_path


class TestAxonometricInfrastructureDrawer(unittest.TestCase):
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
            drawer = AxonometricInfrastructureDrawer(
                self.db, "mercury", filename, "png", self.parameters, None, "yaml"
            )
            drawer.draw()
            self.assertTrue(filename.exists())

    def test_draw_svg(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.svg"
            drawer = AxonometricInfrastructureDrawer(
                self.db, "mercury", filename, "svg", self.parameters, None, "yaml"
            )
            drawer.draw()
            self.assertTrue(filename.exists())

    def test_draw_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.pdf"
            drawer = AxonometricInfrastructureDrawer(
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
                AxonometricInfrastructureDrawer(
                    self.db, "fail", filename, "png", self.parameters, None, "yaml"
                )
            self.assertFalse(filename.exists())

    def test_draw_no_rack_error(self):
        self.parameters.infrastructure.equipment_tags = "fail"
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.png"
            drawer = AxonometricInfrastructureDrawer(
                self.db, "mercury", filename, "png", self.parameters, None, "yaml"
            )
            with self.assertRaisesRegex(
                RacksDBDrawingError,
                "^Unable to find racks to draw with filters provided in drawing "
                "parameters$",
            ):
                drawer.draw()
            self.assertFalse(filename.exists())

    def test_draw_other_racks(self):
        # Mercury infrastructure has multiple racks in rows R1 and R2. With
        # other_racks, all racks of these rows must be selected once.
        self.parameters.infrastructure.other_racks = True
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.png"
            drawer = AxonometricInfrastructureDrawer(
                self.db, "mercury", filename, "png", self.parameters, None, "yaml"
            )
            with self.assertLogs("racksdb.drawers.collisions", "WARNING") as cm:
                drawer.draw()
            self.assertTrue(filename.exists())
        self.assertEqual(
            [rack.name for rack in drawer.racks],
            [f"R{row}-A{idx:02d}" for row in (1, 2) for idx in range(1, 11)],
        )
        self.assertEqual([row.name for row in drawer.rack_rows], ["R1", "R2"])
        # Collision in rack R2-A02 is reported once.
        self.assertEqual(len(cm.output), 1)

    def test_draw_collision(self):
        # In example database, netmercurysw03 switch of sharednet infrastructure
        # collides with swnas01 storage equipment of mercury infrastructure in rack
        # R2-A02.
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.png"
            drawer = AxonometricInfrastructureDrawer(
                self.db, "sharednet", filename, "png", self.parameters, None, "yaml"
            )
            with self.assertLogs("racksdb.drawers.collisions", "WARNING") as cm:
                drawer.draw()
            self.assertTrue(filename.exists())
        self.assertEqual(
            cm.output,
            [
                "WARNING:racksdb.drawers.collisions:Collision detected in rack "
                "R2-A02 between equipment swnas01 (infrastructure mercury) and "
                "netmercurysw03 (infrastructure sharednet)"
            ],
        )
        self.assertEqual(drawer._colliding_equipment, {"netmercurysw03", "swnas01"})
