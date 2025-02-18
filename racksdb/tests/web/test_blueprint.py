# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import tempfile
import json

import flask
import werkzeug
import yaml

from racksdb.web.app import RacksDBWebBlueprint
from racksdb import RacksDB
from racksdb.version import get_version

from ..lib.common import schema_path, db_path, drawing_schema_path

# Expected values from example DB.
EXAMPLE_DATACENTERS = ["paris", "london"]
EXAMPLE_INFRASTRUCTURES = ["mercury", "jupiter", "sharednet"]


class FakeRacksDBWebApp(flask.Flask):
    def __init__(self, schema, db, drawing_schema, openapi):
        super().__init__("Fake RacksDB web application")
        self.blueprint = RacksDBWebBlueprint(
            schema=schema,
            db=db,
            drawings_schema=drawing_schema,
            openapi=openapi,
        )
        self.register_blueprint(self.blueprint)


class RacksDBCustomTestResponse(flask.Response):
    """Custom flask Response class to backport text property of
    werkzeug.test.TestResponse class on werkzeug < 0.15."""

    @property
    def text(self):
        return self.get_data(as_text=True)

    @property
    def json(self):
        if self.mimetype != "application/json":
            return None
        return json.loads(self.text)


class TestRacksDBWebBlueprint(unittest.TestCase):

    def setUp(self):

        try:
            self.schema_path = schema_path()
            self.db_path = db_path()
            self.drawing_schema_path = drawing_schema_path()
        except FileNotFoundError as err:
            self.skipTest(err)
        self.app = FakeRacksDBWebApp(
            self.schema_path, self.db_path, self.drawing_schema_path, True
        )
        self.app.config.update(
            {
                "TESTING": True,
            }
        )

        # werkzeug.test.TestResponse class does not have text and json
        # properties in werkzeug <= 0.15. When such version is installed, use
        # custom test response class to backport these text and json properties.
        try:
            getattr(werkzeug.test.TestResponse, "text")
            getattr(werkzeug.test.TestResponse, "json")
        except AttributeError:
            self.app.response_class = RacksDBCustomTestResponse
        self.client = self.app.test_client()

    def test_openapi(self):
        response = self.client.get("/openapi.yaml")
        self.assertEqual(response.status_code, 200)
        content = yaml.safe_load(response.text)
        self.assertCountEqual(
            content.keys(), ["openapi", "info", "paths", "components"]
        )
        self.assertEqual(content["openapi"], "3.0.0")
        self.assertDictEqual(
            content["info"], {"title": "RacksDB REST API", "version": get_version()}
        )
        self.assertIsInstance(content["paths"], dict)
        self.assertCountEqual(
            content["paths"].keys(),
            [
                f"/v{get_version()}/datacenters",
                f"/v{get_version()}/draw/<entity>/<name>.<format>",
                f"/v{get_version()}/infrastructures",
                f"/v{get_version()}/nodes",
                f"/v{get_version()}/racks",
                f"/v{get_version()}/tags",
            ],
        )
        self.assertIsInstance(content["components"]["schemas"], dict)

    def test_dump(self):
        response = self.client.get(f"/v{get_version()}/dump")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/x-yaml")
        # Check dumped DB can be loaded
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".yml") as tmp:
            tmp.write(response.text)
            db_dumped = RacksDB.load(schema=self.schema_path, db=tmp.name)
        # Compare infrastructure in original and dumped database
        db_orig = RacksDB.load(schema=self.schema_path, db=self.db_path)
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
        response = self.client.get(f"/v{get_version()}/schema")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/x-yaml")
        # Check DB can be loaded with downloaded schema
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".yml") as tmp:
            tmp.write(response.text)
            RacksDB.load(schema=tmp.name, db=self.db_path)

    # test schema

    #
    # datacenters
    #

    def assertDatacentersResponse(self, content):
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 2)
        self.assertCountEqual(
            [datacenter["name"] for datacenter in content], EXAMPLE_DATACENTERS
        )
        self.assertIsInstance(content[0], dict)
        self.assertCountEqual(
            content[0].keys(),
            ["name", "rooms", "tags", "location"],
        )

    def test_datacenters(self):
        response = self.client.get(f"/v{get_version()}/datacenters")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertDatacentersResponse(response.json)

    def test_datacenters_yaml(self):
        response = self.client.get(f"/v{get_version()}/datacenters?format=yaml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/x-yaml")
        self.assertDatacentersResponse(yaml.safe_load(response.text))

    def test_datacenters_list(self):
        response = self.client.get(f"/v{get_version()}/datacenters?list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, EXAMPLE_DATACENTERS)

    def test_datacenters_name(self):
        response = self.client.get(
            f"/v{get_version()}/datacenters?name={EXAMPLE_DATACENTERS[0]}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertCountEqual(response.json[0]["name"], EXAMPLE_DATACENTERS[0])

    def test_datacenters_name_not_found(self):
        response = self.client.get(f"/v{get_version()}/datacenters?name=fail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, [])

    def test_datacenters_tags(self):
        response = self.client.get(f"/v{get_version()}/datacenters?tags=tier2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertCountEqual(response.json[0]["name"], "paris")

    def test_datacenters_tags_not_found(self):
        response = self.client.get(f"/v{get_version()}/datacenters?tags=fail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, [])

    def test_datacenters_fold(self):
        # First try without fold request argument
        response = self.client.get(f"/v{get_version()}/datacenters?name=paris")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json[0]["rooms"][0]["rows"][0]["racks"][0]["name"],
            "R1-A01",
        )
        nb_racks_unfolded = len(response.json[0]["rooms"][0]["rows"][0]["racks"])
        # Then try with fold request argument and compare
        response = self.client.get(f"/v{get_version()}/datacenters?name=paris&fold")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json[0]["rooms"][0]["rows"][0]["racks"][0]["name"],
            "R1-A[01-10]",
        )
        nb_racks_folded = len(response.json[0]["rooms"][0]["rows"][0]["racks"])
        self.assertGreater(nb_racks_unfolded, nb_racks_folded)

    #
    # infrastructures
    #

    def assertInfrastructuresResponse(self, content):
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 3)
        self.assertCountEqual(
            [infrastructure["name"] for infrastructure in content],
            EXAMPLE_INFRASTRUCTURES,
        )
        self.assertIsInstance(content[0], dict)
        self.assertCountEqual(
            content[0].keys(),
            ["name", "description", "layout", "tags"],
        )

    def test_infrastructures(self):
        response = self.client.get(f"/v{get_version()}/infrastructures")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertInfrastructuresResponse(response.json)

    def test_infrastructures_yaml(self):
        response = self.client.get(f"/v{get_version()}/infrastructures?format=yaml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/x-yaml")
        self.assertInfrastructuresResponse(yaml.safe_load(response.text))

    def test_infrastructures_list(self):
        response = self.client.get(f"/v{get_version()}/infrastructures?list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, EXAMPLE_INFRASTRUCTURES)

    def test_infrastructures_name(self):
        response = self.client.get(
            f"/v{get_version()}/infrastructures?name={EXAMPLE_INFRASTRUCTURES[0]}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertEqual(response.json[0]["name"], EXAMPLE_INFRASTRUCTURES[0])

    def test_infrastructures_name_not_found(self):
        response = self.client.get(f"/v{get_version()}/infrastructures?name=fail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, [])

    def test_infrastructures_tags(self):
        response = self.client.get(f"/v{get_version()}/infrastructures?tags=cluster")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 2)
        self.assertCountEqual(
            [infrastructure["name"] for infrastructure in response.json],
            ["mercury", "jupiter"],
        )

    def test_infrastructures_multiple_tags(self):
        response = self.client.get(
            f"/v{get_version()}/infrastructures?tags=cluster,hpc"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertCountEqual(response.json[0]["name"], "mercury")

    def test_infrastructures_tags_not_found(self):
        response = self.client.get(f"/v{get_version()}/infrastructures?tags=fail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, [])

    def test_infrastructures_fold(self):
        # First try without fold request argument
        response = self.client.get(f"/v{get_version()}/infrastructures?name=mercury")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIn(
            response.json[0]["layout"][0]["nodes"][0]["name"],
            [node.name for node in self.app.blueprint.db.nodes],
        )
        nb_nodes_unfolded = len(response.json[0]["layout"][0]["nodes"][0])
        # Then try with fold request argument and compare
        response = self.client.get(
            f"/v{get_version()}/infrastructures?name=mercury&fold"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertNotIn(
            response.json[0]["layout"][0]["nodes"][0]["name"],
            [node.name for node in self.app.blueprint.db.nodes],
        )
        nb_nodes_folded = len(response.json[0]["layout"][0]["nodes"][0])
        self.assertGreater(nb_nodes_unfolded, nb_nodes_folded)

    #
    # nodes
    #

    def assertNodesResponse(self, content):
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 130)
        self.assertIsInstance(content[0], dict)
        self.assertCountEqual(
            content[0].keys(),
            ["name", "infrastructure", "rack", "type", "slot", "tags", "position"],
        )

    def test_nodes(self):
        response = self.client.get(f"/v{get_version()}/nodes")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertNodesResponse(response.json)

    def test_nodes_yaml(self):
        response = self.client.get(f"/v{get_version()}/nodes?format=yaml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/x-yaml")
        self.assertNodesResponse(yaml.safe_load(response.text))

    def test_nodes_list(self):
        response = self.client.get(f"/v{get_version()}/nodes?list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertIsInstance(response.json[0], str)
        self.assertIn(
            response.json[0], [node.name for node in self.app.blueprint.db.nodes]
        )

    def test_nodes_name(self):
        response = self.client.get(f"/v{get_version()}/nodes?name=mecn0003")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "mecn0003")

    def test_nodes_name_not_found(self):
        response = self.client.get(f"/v{get_version()}/nodes?name=fail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, [])

    def test_nodes_tags(self):
        response = self.client.get(f"/v{get_version()}/nodes")
        nb_nodes_total = len(response.json)
        response = self.client.get(f"/v{get_version()}/nodes?tags=compute")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        nb_nodes_tags = len(response.json)
        self.assertGreater(nb_nodes_total, nb_nodes_tags)

    def test_nodes_mulitple_tags(self):
        response = self.client.get(f"/v{get_version()}/nodes?tags=compute")
        nb_nodes_one_tag = len(response.json)
        response = self.client.get(f"/v{get_version()}/nodes?tags=compute,ia")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        nb_nodes_multiple_tags = len(response.json)
        self.assertGreater(nb_nodes_one_tag, nb_nodes_multiple_tags)

    def test_nodes_tags_not_found(self):
        response = self.client.get(f"/v{get_version()}/nodes?tags=fail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, [])

    def test_nodes_fold(self):
        # First try without fold request argument
        response = self.client.get(f"/v{get_version()}/nodes?tags=compute&list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIn(
            response.json[0], [node.name for node in self.app.blueprint.db.nodes]
        )
        nb_nodes_unfolded = len(response.json)
        # Then try with fold request argument and compare
        response = self.client.get(f"/v{get_version()}/nodes?tags=compute&list&fold")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        # FIXME: the first item should be a nodeset
        self.assertIn(
            response.json[0], [node.name for node in self.app.blueprint.db.nodes]
        )
        nb_nodes_folded = len(response.json)
        # FIXME: nb_nodes_unfolded should be greater than nb_nodes_folded
        self.assertEqual(nb_nodes_unfolded, nb_nodes_folded)

    def test_nodes_infrastructure(self):
        # First try without infrastructure request argument
        response = self.client.get(f"/v{get_version()}/nodes")
        nb_nodes_total = len(response.json)
        # Then try with infrastructure request argument and compare
        response = self.client.get(f"/v{get_version()}/nodes?infrastructure=jupiter")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        nb_nodes_infrastructure = len(response.json)
        self.assertGreater(nb_nodes_total, nb_nodes_infrastructure)

    def test_nodes_infrastructure_not_found(self):
        response = self.client.get(f"/v{get_version()}/nodes?infrastructure=fail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, [])

    #
    # racks
    #

    def assertRacksResponse(self, content):
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 101)
        self.assertIsInstance(content[0], dict)
        # tags key is optional, it may not be present in select rack.
        for key in [
            "name",
            "slot",
            "type",
            "datacenter",
            "room",
            "row",
            "nodes",
            "fillrate",
        ]:
            self.assertIn(
                key,
                content[0].keys(),
            )

    def test_racks(self):
        response = self.client.get(f"/v{get_version()}/racks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertRacksResponse(response.json)

    def test_racks_yaml(self):
        response = self.client.get(f"/v{get_version()}/racks?format=yaml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/x-yaml")
        self.assertRacksResponse(yaml.safe_load(response.text))

    def test_racks_list(self):
        response = self.client.get(f"/v{get_version()}/racks?list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertIsInstance(response.json[0], str)
        self.assertIn(
            response.json[0], [rack.name for rack in self.app.blueprint.db.racks]
        )

    def test_racks_name(self):
        response = self.client.get(f"/v{get_version()}/racks?name=R2-A03")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "R2-A03")

    def test_racks_name_not_found(self):
        response = self.client.get(f"/v{get_version()}/racks?name=fail")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, [])

    def test_racks_fold(self):
        # First try without fold request argument
        response = self.client.get(f"/v{get_version()}/racks?list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIn(
            response.json[0], [rack.name for rack in self.app.blueprint.db.racks]
        )
        nb_racks_unfolded = len(response.json)
        # Then try with fold request argument and compare
        response = self.client.get(f"/v{get_version()}/racks?list&fold")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        # FIXME: the first item should be a racksset
        self.assertIn(
            response.json[0], [rack.name for rack in self.app.blueprint.db.racks]
        )
        nb_racks_folded = len(response.json)
        # FIXME: nb_nodes_unfolded should be greater than nb_nodes_folded
        self.assertEqual(nb_racks_unfolded, nb_racks_folded)

    #
    # tags
    #

    def test_tags_node(self):
        response = self.client.get(f"/v{get_version()}/tags?node=mecn0010")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, ["compute"])

    def test_tags_node_yaml(self):
        response = self.client.get(f"/v{get_version()}/tags?node=mecn0010&format=yaml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/x-yaml")
        content = yaml.safe_load(response.text)
        self.assertIsInstance(content, list)
        self.assertCountEqual(content, ["compute"])

    def test_tags_node_not_found(self):
        response = self.client.get(f"/v{get_version()}/tags?node=fail")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 404,
                "description": "Unable to find node fail",
                "name": "Not Found",
            },
        )

    def test_tags_infrastructure(self):
        response = self.client.get(f"/v{get_version()}/tags?infrastructure=mercury")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, ["hpc", "cluster"])

    def test_tags_infrastructure_on_nodes(self):
        response = self.client.get(
            f"/v{get_version()}/tags?infrastructure=mercury&on_nodes"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, ["servers", "compute", "ia", "gpu"])

    def test_tags_infrastructure_not_found(self):
        response = self.client.get(f"/v{get_version()}/tags?infrastructure=fail")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 404,
                "description": "Unable to find infrastructure fail",
                "name": "Not Found",
            },
        )

    def test_tags_datacenter(self):
        response = self.client.get(f"/v{get_version()}/tags?datacenter=paris")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, ["freecooling", "tier2"])

    def test_tags_datacenter_on_racks(self):
        response = self.client.get(f"/v{get_version()}/tags?datacenter=paris&on_racks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertCountEqual(response.json, ["first", "last"])

    def test_tags_datacenter_not_found(self):
        response = self.client.get(f"/v{get_version()}/tags?datacenter=fail")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 404,
                "description": "Unable to find datacenter fail",
                "name": "Not Found",
            },
        )

    def test_tags_missing_parameter(self):
        response = self.client.get(f"/v{get_version()}/tags")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": (
                    "Either node, infrastructure or datacenter parameter must be "
                    "defined to retrieve tags"
                ),
                "name": "Bad Request",
            },
        )
