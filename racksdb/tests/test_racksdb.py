# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import tempfile
import shutil
from pathlib import Path

from racksdb import RacksDB
from racksdb.errors import RacksDBRequestError, RacksDBNotFoundError, RacksDBFormatError

from .lib.common import schema_path, db_path, db_one_file_path


class TestRacksDB(unittest.TestCase):
    def setUp(self):
        try:
            self.schema_path = schema_path()
            self.db_path = db_path()
        except FileNotFoundError as err:
            self.skipTest(err)
        self.db = RacksDB.load(schema=self.schema_path, db=self.db_path)

    def test_content(self):
        self.assertIsInstance(self.db, RacksDB)
        self.assertEqual(len(self.db.infrastructures), 3)
        self.assertEqual(
            type(self.db.infrastructures.first()).__name__, "RacksDBInfrastructure"
        )
        self.assertEqual(self.db.infrastructures["mercury"].name, "mercury")
        self.assertEqual(len(self.db.infrastructures["mercury"].nodes.keys()), 6)
        self.assertEqual(len(self.db.infrastructures["mercury"].nodes), 129)
        self.assertEqual(len(self.db.infrastructures["mercury"].layout[0].nodes), 61)
        self.assertEqual(
            type(self.db.infrastructures["mercury"].nodes["mecn0001"]).__name__,
            "RacksDBNode",
        )
        self.assertEqual(
            self.db.infrastructures["mercury"].nodes["mecn0001"].name, "mecn0001"
        )
        self.assertEqual(
            self.db.infrastructures["mercury"].nodes["mecn0001"].type.model,
            "SuperMicro A+ Server 2124BT-HTR",
        )
        self.assertEqual(
            self.db.infrastructures["mercury"].nodes["mecn0010"]._first.name, "mecn0001"
        )
        self.assertEqual(
            self.db.infrastructures["mercury"].nodes["mecn0010"].tags, ["compute"]
        )
        node = self.db.infrastructures["mercury"].nodes["mecn0001"]
        self.assertEqual(node, node._first)

    def test_nodes(self):
        # Thanks to lazy loading, just a few expandable object are loaded, much
        # fewer than the number of nodes. The number of potentially expanded
        # objects is reported correctly by len(). However, it must be much lower
        # than the actual number of keys/values in the dictionnary.
        self.assertEqual(len(self.db.nodes.keys()), 7)
        self.assertEqual(len(self.db.nodes), 130)

    def test_racks(self):
        self.assertEqual(len(self.db.racks), 101)
        self.assertEqual(
            self.db.racks[0].name,
            self.db.datacenters.first()
            .rooms.first()
            .rows.first()
            .racks[0]
            .objects()[0]
            .name,
        )

    def test_tags_missing_param(self):
        msg = (
            "^Either node, infrastructure or datacenter parameter must be defined to "
            "retrieve tags$"
        )
        with self.assertRaisesRegex(RacksDBRequestError, msg):
            self.db.tags()
        with self.assertRaisesRegex(RacksDBRequestError, msg):
            self.db.tags(None, None, None)
        with self.assertRaisesRegex(RacksDBRequestError, msg):
            self.db.tags(node=None, infrastructure=None, datacenter=None)

    def test_tags_node(self):
        self.assertCountEqual(self.db.tags(node="megpu0001"), ["gpu", "ia"])
        self.assertCountEqual(self.db.tags(node="mecn0001"), ["compute"])

    def test_tags_node_not_found(self):
        with self.assertRaisesRegex(RacksDBNotFoundError, "^Unable to find node fail$"):
            self.db.tags(node="fail")

    def test_tags_infrastructure(self):
        self.assertCountEqual(
            self.db.tags(infrastructure="mercury"), ["hpc", "cluster"]
        )
        self.assertCountEqual(
            self.db.tags(infrastructure="jupiter"), ["data", "cluster"]
        )
        self.assertCountEqual(self.db.tags(infrastructure="sharednet"), [])

    def test_tags_infrastructure_on_nodes(self):
        self.assertCountEqual(
            self.db.tags(infrastructure="mercury", on_nodes=True),
            ["compute", "servers", "ia", "gpu"],
        )
        self.assertCountEqual(self.db.tags(infrastructure="jupiter", on_nodes=True), [])

    def test_tags_infrastructure_not_found(self):
        with self.assertRaisesRegex(
            RacksDBNotFoundError, "^Unable to find infrastructure fail$"
        ):
            self.db.tags(infrastructure="fail")

    def test_tags_datacenter(self):
        self.assertCountEqual(
            self.db.tags(datacenter="paris"), ["freecooling", "tier2"]
        )
        self.assertCountEqual(
            self.db.tags(datacenter="london"), ["freecooling", "tier3"]
        )

    def test_tags_datacenter_on_racks(self):
        self.assertCountEqual(
            self.db.tags(datacenter="paris", on_racks=True), ["first", "last"]
        )
        self.assertCountEqual(self.db.tags(datacenter="london", on_racks=True), [])

    def test_tags_datacenter_not_found(self):
        with self.assertRaisesRegex(
            RacksDBNotFoundError, "^Unable to find datacenter fail$"
        ):
            self.db.tags(datacenter="fail")


class TestRacksDBAlternatePaths(unittest.TestCase):
    def test_db_ext_yml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            new_db_path = Path(tmpdir) / "db.yml"
            shutil.copyfile(db_one_file_path(), new_db_path)
            self.db = RacksDB.load(schema=schema_path(), db=new_db_path)

    def test_db_ext_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            new_db_path = Path(tmpdir) / "db.yaml"
            shutil.copyfile(db_one_file_path(), new_db_path)
            self.db = RacksDB.load(schema=schema_path(), db=new_db_path)

    def test_db_ext_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            new_db_path = Path(tmpdir) / "db.fail"
            shutil.copyfile(db_one_file_path(), new_db_path)
            with self.assertRaisesRegex(
                RacksDBFormatError,
                r"^DB contains file \/.*\/db\.fail without valid extensions: .*$",
            ):
                RacksDB.load(schema=schema_path(), db=new_db_path)
