# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import unittest
from unittest import mock
import tempfile
from pathlib import Path
from types import SimpleNamespace

from racksdb import RacksDB
from racksdb.drawers.infrastructure import InfrastructureDrawer, equipment_overlap
from racksdb.drawers.parameters import DrawingParameters
from racksdb.generic.db import DBDictsLoader
from racksdb.errors import RacksDBDrawingError

from ..lib.common import drawing_schema_path, schema_path, db_path


def equipment(height, size=1, width_position=0, width=1.0):
    """Return a fake equipment located at the given height (in rack units) with the
    given size (in rack units) and the given position in rack width for the given
    width (fraction of rack width)."""
    return SimpleNamespace(
        position=SimpleNamespace(height=height, width=width_position),
        type=SimpleNamespace(height=size, width=width),
    )


class TestEquipmentOverlap(unittest.TestCase):
    def test_overlap(self):
        self.assertTrue(equipment_overlap(equipment(0, 2), equipment(1, 2)))

    def test_same_position(self):
        self.assertTrue(equipment_overlap(equipment(3), equipment(3)))

    def test_included(self):
        self.assertTrue(equipment_overlap(equipment(0, 4), equipment(1)))

    def test_disjoint(self):
        self.assertFalse(equipment_overlap(equipment(0), equipment(5)))

    def test_stacked(self):
        self.assertFalse(equipment_overlap(equipment(0, 2), equipment(2, 2)))
        self.assertFalse(equipment_overlap(equipment(2, 2), equipment(0, 2)))

    def test_side_by_side(self):
        self.assertFalse(
            equipment_overlap(equipment(0, 1, 0, 0.5), equipment(0, 1, 1, 0.5))
        )
        # Third widths are not exactly representable with floats.
        self.assertFalse(
            equipment_overlap(equipment(0, 1, 1, 1 / 3), equipment(0, 1, 2, 1 / 3))
        )

    def test_partial_width(self):
        # Full width equipment overlaps half width equipment at the same height.
        self.assertTrue(equipment_overlap(equipment(0), equipment(0, 1, 1, 0.5)))
        # Half width and third width equipment overlap on the left side.
        self.assertTrue(
            equipment_overlap(equipment(0, 1, 0, 0.5), equipment(0, 1, 1, 1 / 3))
        )
        # Half width on the right side and third width on the left do not overlap.
        self.assertFalse(
            equipment_overlap(equipment(0, 1, 1, 0.5), equipment(0, 1, 0, 1 / 3))
        )


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

    def test_draw_no_rack_error(self):
        self.parameters.infrastructure.equipment_tags = "fail"
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.png"
            drawer = InfrastructureDrawer(
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
            drawer = InfrastructureDrawer(
                self.db, "mercury", filename, "png", self.parameters, None, "yaml"
            )
            with self.assertLogs("racksdb.drawers.infrastructure", "WARNING") as cm:
                drawer.draw()
            self.assertTrue(filename.exists())
        self.assertEqual(
            [rack.name for rack in drawer.racks],
            [f"R{row}-A{idx:02d}" for row in (1, 2) for idx in range(1, 11)],
        )
        self.assertEqual([row.name for row in drawer.rack_rows], ["R1", "R2"])
        # Collision in rack R2-A02 is reported once.
        self.assertEqual(len(cm.output), 1)

    def _equipment_definition(self, infrastructure, rack, name):
        """Return the definition (ie. not expanded) of an equipment in database."""
        for _infrastructure in self.db.infrastructures:
            if _infrastructure.name != infrastructure:
                continue
            for part in _infrastructure.layout:
                if part.rack.name != rack:
                    continue
                for equipments in (part.nodes, part.storage, part.network, part.misc):
                    for definition in equipments.values():
                        if str(definition.name) == name:
                            return definition
        raise KeyError(name)

    def _draw_with_logs(self, drawer):
        with tempfile.TemporaryDirectory() as tmpdir:
            drawer.file = Path(tmpdir) / "output.png"
            with self.assertLogs("racksdb.drawers.infrastructure", "WARNING") as cm:
                drawer.draw()
            self.assertTrue(drawer.file.exists())
        return cm.output

    def test_no_collision(self):
        # Move netmercurysw03 switch in a free slot to remove the collision in
        # example database.
        self._equipment_definition("sharednet", "R2-A02", "netmercurysw03").slot = 16
        drawer = InfrastructureDrawer(
            self.db, "mercury", "dontmind.png", "png", self.parameters, None, "yaml"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            drawer.file = Path(tmpdir) / "output.png"
            # Mock logger to check no warning is emitted, unittest assertNoLogs() is
            # not available in Python < 3.10.
            with mock.patch("racksdb.drawers.infrastructure.logger") as logger:
                drawer.draw()
        logger.warning.assert_not_called()
        self.assertEqual(drawer._colliding_equipment, set())

    def test_collision_other_infrastructure(self):
        # In example database, netmercurysw03 switch of sharednet infrastructure
        # collides with swnas01 storage equipment of mercury infrastructure in rack
        # R2-A02. It must be reported when drawing both infrastructures.
        for infrastructure in ["mercury", "sharednet"]:
            with self.subTest(infrastructure=infrastructure):
                drawer = InfrastructureDrawer(
                    self.db,
                    infrastructure,
                    "dontmind.png",
                    "png",
                    self.parameters,
                    None,
                    "yaml",
                )
                output = self._draw_with_logs(drawer)
                self.assertEqual(
                    output,
                    [
                        "WARNING:racksdb.drawers.infrastructure:Collision detected in "
                        "rack R2-A02 between equipment swnas01 (infrastructure "
                        "mercury) and netmercurysw03 (infrastructure sharednet)"
                    ],
                )
                self.assertEqual(
                    drawer._colliding_equipment, {"netmercurysw03", "swnas01"}
                )

    def test_collision_same_infrastructure(self):
        # Move mekvm01 one slot below, at the same height as mesrv0004 upper half.
        self._equipment_definition("mercury", "R2-A03", "mekvm01").slot = 16
        drawer = InfrastructureDrawer(
            self.db, "mercury", "dontmind.png", "png", self.parameters, None, "yaml"
        )
        output = self._draw_with_logs(drawer)
        self.assertIn(
            "WARNING:racksdb.drawers.infrastructure:Collision detected in rack R2-A03 "
            "between equipment mesrv0004 (infrastructure mercury) and mekvm01 "
            "(infrastructure mercury)",
            output,
        )
        self.assertEqual(
            drawer._colliding_equipment,
            {"netmercurysw03", "swnas01", "mesrv0004", "mekvm01"},
        )
