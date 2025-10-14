# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from unittest import mock
import io
import tempfile
import json
from pathlib import Path
import os
import mimetypes

import yaml

from racksdb import RacksDB
from racksdb.exec import RacksDBExec
from racksdb.version import get_version

from .lib.common import schema_path, db_path, drawing_schema_path
from .lib.reference import (
    TestRacksDBReferenceDB,
    REFDB_INFRASTRUCTURES,
    REFDB_DATACENTERS,
    REFDB_TOTAL_NODES,
)


CMD_BASE_ARGS = ["--schema", str(schema_path()), "--db", str(db_path())]
CMD_DRAW_BASE_ARGS = ["draw", "--drawings-schema", str(drawing_schema_path())]


class TestRacksDBExec(TestRacksDBReferenceDB):
    def test_version(self):
        for option in ["-v", "--version"]:
            with mock.patch("sys.stdout", new=io.StringIO()) as output:
                with self.assertRaisesRegex(SystemExit, "0"):
                    RacksDBExec([option])
                self.assertEqual(output.getvalue(), f"RacksDB {get_version()}\n")

    def test_dump(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(CMD_BASE_ARGS + ["dump"])
            # Check dumped DB can be loaded
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".yml") as tmp:
                tmp.write(output.getvalue())
                tmp.flush()  # Make sure file is written to disk
                db_dumped = RacksDB.load(schema=schema_path(), db=tmp.name)
        # Compare infrastructure in original and dumped database
        db_orig = RacksDB.load(schema=schema_path(), db=db_path())
        self.assertCountEqual(
            [
                infrastructure.name
                for infrastructure in db_orig.infrastructures.values()
            ],
            [
                infrastructure.name
                for infrastructure in db_dumped.infrastructures.values()
            ],
        )

    def test_schema(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(CMD_BASE_ARGS + ["schema"])
            # Check DB can be loaded with schema in output
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".yml") as tmp:
                tmp.write(output.getvalue())
                tmp.flush()  # Make sure file is written to disk
                RacksDB.load(schema=tmp.name, db=db_path())

    #
    # datacenters
    #

    def test_datacenters(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(CMD_BASE_ARGS + ["datacenters"])
            self.assertDatacentersResponse(yaml.safe_load(output.getvalue()))

    def test_datacenters_json(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "datacenters",
                    "--format",
                    "json",
                ]
            )
            self.assertDatacentersResponse(json.loads(output.getvalue()))

    def test_datacenters_list(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "datacenters",
                    "--list",
                ]
            )
            self.assertCountEqual(
                output.getvalue().strip().split("\n"), REFDB_DATACENTERS
            )

    def test_datacenters_not_found(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "datacenters",
                    "--name",
                    "fail",
                ]
            )
            self.assertEqual(output.getvalue(), "[]\n")

    #
    # infrastructures
    #

    def test_infrastructures(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "infrastructures",
                ]
            )
            self.assertInfrastructuresResponse(yaml.safe_load(output.getvalue()))

    def test_infrastructures_json(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "infrastructures",
                    "--format",
                    "json",
                ]
            )
            self.assertInfrastructuresResponse(json.loads(output.getvalue()))

    def test_infrastructure_list(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "infrastructures",
                    "--list",
                ]
            )
            self.assertCountEqual(
                output.getvalue().strip().split("\n"), REFDB_INFRASTRUCTURES
            )

    def test_infrastructure_not_found(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "infrastructures",
                    "--name",
                    "fail",
                ]
            )
            self.assertEqual(output.getvalue(), "[]\n")

    #
    # nodes
    #

    def test_nodes(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                ]
            )
            self.assertNodesResponse(yaml.safe_load(output.getvalue()))

    def test_nodes_json(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                    "--format",
                    "json",
                ]
            )
            self.assertNodesResponse(json.loads(output.getvalue()))

    def test_nodes_list(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                    "--list",
                ]
            )
            self.assertEqual(
                len(output.getvalue().strip().split("\n")), REFDB_TOTAL_NODES
            )

    def test_nodes_name(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                    "--name",
                    "mecn0005",
                ]
            )
            nodes = yaml.safe_load(output.getvalue())
            self.assertIsInstance(nodes, list)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0]["name"], "mecn0005")

    def test_nodes_not_found(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                    "--name",
                    "fail",
                ]
            )
            self.assertEqual(output.getvalue(), "[]\n")

    def test_nodes_tags(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                    "--tags",
                    "compute",
                ]
            )
            nodes = yaml.safe_load(output.getvalue())
            self.assertIsInstance(nodes, list)
            self.assertLess(len(nodes), REFDB_TOTAL_NODES)

    def test_nodes_multiple_tags(self):
        # Check less nodes are selected with multiple tags than with only one tag.
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                    "--tags",
                    "compute",
                ]
            )
            nodes_one_tag = yaml.safe_load(output.getvalue())
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                    "--tags",
                    "compute",
                    "ia",
                ]
            )
            nodes_multiple_tags = yaml.safe_load(output.getvalue())
        self.assertLess(len(nodes_multiple_tags), len(nodes_one_tag))

    def test_nodes_fold(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                    "--list",
                ]
            )
            unfolded = output.getvalue().strip().split("\n")
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "nodes",
                    "--list",
                    "--fold",
                ]
            )
            folded = output.getvalue().strip().split("\n")
            self.assertEqual(len(folded), 1)
            self.assertGreater(len(unfolded), len(folded))

    #
    # racks
    #

    def test_racks(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "racks",
                ]
            )
            self.assertRacksResponse(yaml.safe_load(output.getvalue()))

    def test_racks_json(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "racks",
                    "--format",
                    "json",
                ]
            )
            self.assertRacksResponse(json.loads(output.getvalue()))

    def test_racks_list(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "racks",
                    "--list",
                ]
            )
            self.assertEqual(len(output.getvalue().strip().split("\n")), 101)

    def test_racks_not_found(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "racks",
                    "--name",
                    "fail",
                ]
            )
            self.assertEqual(output.getvalue(), "[]\n")

    def test_racks_fold(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "racks",
                    "--list",
                ]
            )
            unfolded = output.getvalue().strip().split("\n")
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS
                + [
                    "racks",
                    "--list",
                    "--fold",
                ]
            )
            folded = output.getvalue().strip().split("\n")
            self.assertEqual(len(folded), 1)
            self.assertGreater(len(unfolded), len(folded))

    #
    # tags
    #

    def test_tags_node(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(CMD_BASE_ARGS + ["tags", "--node", "mecn0001"])
            tags = output.getvalue().strip().split("\n")
            self.assertCountEqual(tags, ["compute"])

    def test_tags_node_not_found(self):
        with mock.patch("sys.stderr", new=io.StringIO()) as errors:
            with self.assertRaisesRegex(SystemExit, "1"):
                RacksDBExec(CMD_BASE_ARGS + ["tags", "--node", "fail"])
            self.assertIn("Unable to find node fail", errors.getvalue())

    def test_tags_infrastructure(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(CMD_BASE_ARGS + ["tags", "--infrastructure", "mercury"])
            tags = output.getvalue().strip().split("\n")
            self.assertCountEqual(tags, ["hpc", "cluster"])

    def test_tags_infrastructure_on_nodes(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(
                CMD_BASE_ARGS + ["tags", "--infrastructure", "mercury", "--on-nodes"]
            )
            tags = output.getvalue().strip().split("\n")
            self.assertCountEqual(tags, ["compute", "servers", "ia", "gpu"])

    def test_tags_infrastructure_not_found(self):
        with mock.patch("sys.stderr", new=io.StringIO()) as errors:
            with self.assertRaisesRegex(SystemExit, "1"):
                RacksDBExec(CMD_BASE_ARGS + ["tags", "--infrastructure", "fail"])
            self.assertIn("Unable to find infrastructure fail", errors.getvalue())

    def test_tags_datacenter(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(CMD_BASE_ARGS + ["tags", "--datacenter", "paris"])
            tags = output.getvalue().strip().split("\n")
            self.assertCountEqual(tags, ["freecooling", "tier2"])

    def test_tags_datacenter_on_racks(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as output:
            RacksDBExec(CMD_BASE_ARGS + ["tags", "--datacenter", "paris", "--on-racks"])
            tags = output.getvalue().strip().split("\n")
            self.assertCountEqual(tags, ["first", "last"])

    def test_tags_datacenter_not_found(self):
        with mock.patch("sys.stderr", new=io.StringIO()) as errors:
            with self.assertRaisesRegex(SystemExit, "1"):
                RacksDBExec(CMD_BASE_ARGS + ["tags", "--datacenter", "fail"])
            self.assertIn("Unable to find datacenter fail", errors.getvalue())

    def test_tags_missing_option(self):
        with mock.patch("sys.stderr", new=io.StringIO()) as errors:
            with self.assertRaisesRegex(SystemExit, "1"):
                RacksDBExec(CMD_BASE_ARGS + ["tags"])
            self.assertIn(
                "Either --node, --infrastructure or --datacenter is required",
                errors.getvalue(),
            )

    #
    # draw
    #
    def test_draw_room(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / "noisy.png"
                os.chdir(tmpdir)
                RacksDBExec(
                    CMD_BASE_ARGS + CMD_DRAW_BASE_ARGS + ["room", "--name", "noisy"]
                )
                self.assertTrue(drawing.exists())
        finally:
            os.chdir(cwd)

    def drawExpectMimetype(self, img_format, expected_mimetype):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / f"noisy.{img_format}"
                os.chdir(tmpdir)
                RacksDBExec(
                    CMD_BASE_ARGS
                    + CMD_DRAW_BASE_ARGS
                    + ["room", "--name", "noisy", "--format", img_format]
                )
                self.assertTrue(drawing.exists())
                self.assertEqual(
                    mimetypes.guess_type(str(drawing))[0], expected_mimetype
                )
        finally:
            os.chdir(cwd)

    def test_draw_png(self):
        self.drawExpectMimetype("png", "image/png")

    def test_draw_pdf(self):
        self.drawExpectMimetype("pdf", "application/pdf")

    def test_draw_svg(self):
        self.drawExpectMimetype("svg", "image/svg+xml")

    def test_draw_unsupported_format(self):
        with self.assertRaisesRegex(SystemExit, "2"):
            RacksDBExec(
                CMD_BASE_ARGS
                + CMD_DRAW_BASE_ARGS
                + ["room", "--name", "noisy", "--format", "fail"]
            )

    def test_draw_with_drawing_parameters(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / "noisy.png"
                params = Path(tmpdir) / "params.yml"
                with open(params, "w+") as fh:
                    fh.write(yaml.dump({"margin": {"left": 10, "top": 10}}))
                os.chdir(tmpdir)
                RacksDBExec(
                    CMD_BASE_ARGS
                    + CMD_DRAW_BASE_ARGS
                    + ["room", "--name", "noisy", "--parameters", str(params)]
                )
                self.assertTrue(drawing.exists())
        finally:
            os.chdir(cwd)

    def test_draw_with_drawing_parameters_stdin(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / "noisy.png"
                os.chdir(tmpdir)
                with mock.patch("sys.stdin.read") as stdin:
                    stdin.return_value = yaml.dump({"margin": {"left": 10, "top": 10}})
                    RacksDBExec(
                        CMD_BASE_ARGS
                        + CMD_DRAW_BASE_ARGS
                        + ["room", "--name", "noisy", "--parameters=-"]
                    )
                self.assertTrue(drawing.exists())
        finally:
            os.chdir(cwd)

    def test_draw_with_invalid_drawing_parameters(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / "noisy.png"
                params = Path(tmpdir) / "params.yml"
                with open(params, "w+") as fh:
                    fh.write(yaml.dump({"fail": True}))
                os.chdir(tmpdir)
                with mock.patch("sys.stderr", new=io.StringIO()) as errors:
                    with self.assertRaisesRegex(SystemExit, "1"):
                        RacksDBExec(
                            CMD_BASE_ARGS
                            + CMD_DRAW_BASE_ARGS
                            + ["room", "--name", "noisy", "--parameters", str(params)]
                        )
                    self.assertIn(
                        "Unable to load drawing parameters", errors.getvalue()
                    )
                self.assertFalse(drawing.exists())
        finally:
            os.chdir(cwd)

    def test_draw_room_not_found(self):
        with mock.patch("sys.stderr", new=io.StringIO()) as errors:
            with self.assertRaisesRegex(SystemExit, "1"):
                RacksDBExec(
                    CMD_BASE_ARGS + CMD_DRAW_BASE_ARGS + ["room", "--name", "fail"]
                )
            self.assertIn("Unable to find room fail in database", errors.getvalue())

    def test_draw_infrastructure(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / "mercury.png"
                os.chdir(tmpdir)
                RacksDBExec(
                    CMD_BASE_ARGS
                    + CMD_DRAW_BASE_ARGS
                    + ["infrastructure", "--name", "mercury"]
                )
                self.assertTrue(drawing.exists())
        finally:
            os.chdir(cwd)

    def test_draw_infrastructure_not_found(self):
        with mock.patch("sys.stderr", new=io.StringIO()) as errors:
            with self.assertRaisesRegex(SystemExit, "1"):
                RacksDBExec(
                    CMD_BASE_ARGS
                    + CMD_DRAW_BASE_ARGS
                    + ["infrastructure", "--name", "fail"]
                )
            self.assertIn(
                "Unable to find infrastructure fail in database", errors.getvalue()
            )

    def test_draw_infrastructure_with_coordinates(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / "mercury.png"
                coordinates = Path(tmpdir) / "coordinates.json"
                os.chdir(tmpdir)
                RacksDBExec(
                    CMD_BASE_ARGS
                    + CMD_DRAW_BASE_ARGS
                    + ["infrastructure", "--name", "mercury", "--coordinates"]
                )
                self.assertTrue(drawing.exists())
                self.assertTrue(coordinates.exists())
                # check valid json
                with open(coordinates) as fh:
                    content = json.loads(fh.read())
                    self.assertIsInstance(content, dict)
        finally:
            os.chdir(cwd)

    def test_draw_infrastructure_with_coordinates_yaml(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / "mercury.png"
                coordinates = Path(tmpdir) / "coordinates.yaml"
                os.chdir(tmpdir)
                RacksDBExec(
                    CMD_BASE_ARGS
                    + CMD_DRAW_BASE_ARGS
                    + [
                        "infrastructure",
                        "--name",
                        "mercury",
                        "--coordinates",
                        "--coordinates-format",
                        "yaml",
                    ]
                )
                self.assertTrue(drawing.exists())
                self.assertTrue(coordinates.exists())
                # check valid yaml
                with open(coordinates) as fh:
                    content = yaml.safe_load(fh.read())
                    self.assertIsInstance(content, dict)
        finally:
            os.chdir(cwd)

    def test_draw_infrastructure_with_coordinates_custom_file(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / "mercury.png"
                coordinates = Path(tmpdir) / "custom-coordinates.json"
                os.chdir(tmpdir)
                RacksDBExec(
                    CMD_BASE_ARGS
                    + CMD_DRAW_BASE_ARGS
                    + [
                        "infrastructure",
                        "--name",
                        "mercury",
                        "--coordinates",
                        str(coordinates),
                    ]
                )
                self.assertTrue(drawing.exists())
                self.assertTrue(coordinates.exists())
        finally:
            os.chdir(cwd)

    def test_draw_infrastructure_axonometric(self):
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                drawing = Path(tmpdir) / "mercury.png"
                params = Path(tmpdir) / "params.yml"
                with open(params, "w+") as fh:
                    fh.write(yaml.dump({"axonometric": {"enabled": True}}))
                os.chdir(tmpdir)
                RacksDBExec(
                    CMD_BASE_ARGS
                    + CMD_DRAW_BASE_ARGS
                    + [
                        "infrastructure",
                        "--name",
                        "mercury",
                        "--parameters",
                        str(params),
                    ]
                )
                self.assertTrue(drawing.exists())
        finally:
            os.chdir(cwd)

    #
    # autopaging
    #

    def test_autopager_used_in_schema(self):
        with mock.patch("racksdb.exec.AutoPager") as autopager:
            with mock.patch("sys.stdout", new=io.StringIO()):
                RacksDBExec(CMD_BASE_ARGS + ["schema"])
            autopager.assert_called_once()
            # Ensure context manager was entered
            autopager.return_value.__enter__.assert_called_once()

    def test_autopager_used_in_dump(self):
        with mock.patch("racksdb.exec.AutoPager") as autopager:
            with mock.patch("sys.stdout", new=io.StringIO()):
                RacksDBExec(CMD_BASE_ARGS + ["dump"])
            autopager.assert_called_once()
            autopager.return_value.__enter__.assert_called_once()

    def test_autopager_used_in_views(self):
        # Use a representative view command that goes through _dump_view
        with mock.patch("racksdb.exec.AutoPager") as autopager:
            with mock.patch("sys.stdout", new=io.StringIO()):
                RacksDBExec(CMD_BASE_ARGS + ["datacenters"])
            autopager.assert_called_once()
            autopager.return_value.__enter__.assert_called_once()
