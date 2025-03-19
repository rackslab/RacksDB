# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import yaml
from pathlib import Path
import tempfile

from racksdb.generic.db import DBDictsLoader, DBSplittedFilesLoader
from racksdb.drawers.parameters import DrawingParameters
from racksdb.generic.errors import DBFormatError
from ..lib.common import drawing_schema_path


class TestRacksDBDrawingParameters(unittest.TestCase):
    def test_load(self):
        DrawingParameters.load(DBDictsLoader(), drawing_schema_path())

    def test_load_ext_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            drawing_parameters_db_path = Path(tmpdir) / "params.yaml"
            with open(drawing_parameters_db_path, "w+") as fh:
                fh.write(yaml.dump({"margin": {"left": 10, "top": 10}}))
            DrawingParameters.load(
                DBSplittedFilesLoader(drawing_parameters_db_path), drawing_schema_path()
            )

    def test_load_ext_yml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            drawing_parameters_db_path = Path(tmpdir) / "params.yml"
            with open(drawing_parameters_db_path, "w+") as fh:
                fh.write(yaml.dump({"margin": {"left": 10, "top": 10}}))
            DrawingParameters.load(
                DBSplittedFilesLoader(drawing_parameters_db_path), drawing_schema_path()
            )

    def test_load_ext_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            drawing_parameters_db_path = Path(tmpdir) / "params.fail"
            with open(drawing_parameters_db_path, "w+") as fh:
                fh.write(yaml.dump({"margin": {"left": 10, "top": 10}}))
            # FIXME: should raise RacksDBFormatError
            with self.assertRaisesRegex(
                DBFormatError,
                r"^DB contains file \/.*\/params\.fail without valid extensions: .*$",
            ):
                DrawingParameters.load(
                    DBSplittedFilesLoader(drawing_parameters_db_path),
                    drawing_schema_path(),
                )
