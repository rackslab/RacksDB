# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
import json
import parameterized

import werkzeug
import yaml
import flask
from requests_toolbelt import MultipartDecoder

from racksdb.web.app import RacksDBWebBlueprint
from racksdb import RacksDB
from racksdb.version import get_version

from ..lib.web import RacksDBCustomTestResponse
from ..lib.common import schema_path, db_path, drawing_schema_path
from ..lib.reference import (
    TestRacksDBReferenceDB,
    REFDB_DATACENTERS,
    REFDB_INFRASTRUCTURES,
)


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


class TestRacksDBWebBlueprint(TestRacksDBReferenceDB):
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

    #
    # datacenters
    #

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
        self.assertCountEqual(response.json, REFDB_DATACENTERS)

    def test_datacenters_name(self):
        response = self.client.get(
            f"/v{get_version()}/datacenters?name={REFDB_DATACENTERS[0]}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertCountEqual(response.json[0]["name"], REFDB_DATACENTERS[0])

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
        self.assertCountEqual(response.json, REFDB_INFRASTRUCTURES)

    def test_infrastructures_name(self):
        response = self.client.get(
            f"/v{get_version()}/infrastructures?name={REFDB_INFRASTRUCTURES[0]}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, list)
        self.assertEqual(response.json[0]["name"], REFDB_INFRASTRUCTURES[0])

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
    # draw
    #

    def client_method(self, verb):
        return self.client.get if verb == "get" else self.client.post

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_room_png(self, verb):
        response = self.client_method(verb)(f"/v{get_version()}/draw/room/noisy.png")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_room_svg(self, verb):
        response = self.client_method(verb)(f"/v{get_version()}/draw/room/noisy.svg")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/svg+xml")

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_room_pdf(self, verb):
        response = self.client_method(verb)(f"/v{get_version()}/draw/room/noisy.pdf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_room_invalid(self, verb):
        response = self.client_method(verb)(f"/v{get_version()}/draw/room/fail.png")
        self.assertEqual(response.status_code, 400)  # FIXME: should be HTTP/404
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": "Unable to find room fail in database",
                "name": "Bad Request",
            },
        )

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_room_coordinates(self, verb):
        response = self.client_method(verb)(
            f"/v{get_version()}/draw/room/noisy.png?coordinates"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "multipart/form-data")
        decoder = MultipartDecoder(response.get_data(), response.content_type)
        (image_part, coordinates_part) = decoder.parts
        self.assertEqual(image_part.headers.get(b"Content-Type").decode(), "image/png")
        self.assertEqual(
            coordinates_part.headers.get(b"Content-Type").decode(), "application/json"
        )
        coordinates = json.loads(coordinates_part.text)
        self.assertEqual(coordinates, {})  # FIXME: room coordinates are empty

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_room_coordinates_yaml(self, verb):
        response = self.client_method(verb)(
            f"/v{get_version()}/draw/room/noisy.png?coordinates&coordinates_format=yaml"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "multipart/form-data")
        decoder = MultipartDecoder(response.get_data(), response.content_type)
        (image_part, coordinates_part) = decoder.parts
        self.assertEqual(image_part.headers.get(b"Content-Type").decode(), "image/png")
        self.assertEqual(
            coordinates_part.headers.get(b"Content-Type").decode(), "application/x-yaml"
        )
        coordinates = yaml.safe_load(coordinates_part.text)
        self.assertEqual(coordinates, {})  # FIXME: room coordinates are empty

    def test_draw_get_room_parameters(self):
        response = self.client.get(
            f"/v{get_version()}/draw/room/noisy.png?"
            "parameters.margin.left=10&parameters.margin.top=10"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_draw_post_room_parameters(self):
        drawing_parameters = {"margin": {"left": 10, "top": 10}}
        response = self.client.post(
            f"/v{get_version()}/draw/room/noisy.png",
            data=json.dumps(drawing_parameters),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_draw_post_room_parameters_yaml(self):
        drawing_parameters = {"margin": {"left": 10, "top": 10}}
        response = self.client.post(
            f"/v{get_version()}/draw/room/noisy.png",
            data=yaml.dump(drawing_parameters),
            content_type="application/x-yaml",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_draw_get_room_invalid_parameters(self):
        response = self.client.get(
            f"/v{get_version()}/draw/room/noisy.png?parameters.fail=true"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": (
                    "Unable to load drawing parameters: Property fail is not defined "
                    "in schema for object Schema_content"
                ),
                "name": "Bad Request",
            },
        )

    def test_draw_post_room_invalid_parameters(self):
        drawing_parameters = {"fail": True}
        response = self.client.post(
            f"/v{get_version()}/draw/room/noisy.png",
            data=json.dumps(drawing_parameters),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": (
                    "Unable to load drawing parameters: Property fail is not defined "
                    "in schema for object Schema_content"
                ),
                "name": "Bad Request",
            },
        )

    def test_draw_post_room_ignored_query_parameters(self):
        response = self.client.post(
            f"/v{get_version()}/draw/room/noisy.png?parameters.fail=true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_draw_post_room_parameters_invalid_format(self):
        response = self.client.post(
            f"/v{get_version()}/draw/room/noisy.png",
            data="fail",
            content_type="text/html",
        )
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 415,
                "description": "Unsupported request body format",
                "name": "Unsupported Media Type",
            },
        )

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_infrastructure_png(self, verb):
        response = self.client_method(verb)(
            f"/v{get_version()}/draw/infrastructure/mercury.png"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_infrastructure_svg(self, verb):
        response = self.client_method(verb)(
            f"/v{get_version()}/draw/infrastructure/mercury.svg"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/svg+xml")

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_infrastructure_pdf(self, verb):
        response = self.client_method(verb)(
            f"/v{get_version()}/draw/infrastructure/mercury.pdf"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_infrastructure_invalid(self, verb):
        response = self.client_method(verb)(
            f"/v{get_version()}/draw/infrastructure/fail.png"
        )
        self.assertEqual(response.status_code, 400)  # FIXME: should be HTTP/404
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": "Unable to find infrastructure fail in database",
                "name": "Bad Request",
            },
        )

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_infrastructure_coordinates(self, verb):
        response = self.client_method(verb)(
            f"/v{get_version()}/draw/infrastructure/mercury.png?coordinates"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "multipart/form-data")
        decoder = MultipartDecoder(response.get_data(), response.content_type)
        (image_part, coordinates_part) = decoder.parts
        self.assertEqual(image_part.headers.get(b"Content-Type").decode(), "image/png")
        self.assertEqual(
            coordinates_part.headers.get(b"Content-Type").decode(), "application/json"
        )
        coordinates = json.loads(coordinates_part.text)
        self.assertIn("mecn0001", coordinates)

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_infrastructure_coordinates_yaml(self, verb):
        response = self.client_method(verb)(
            f"/v{get_version()}/draw/infrastructure/mercury.png?coordinates&"
            "coordinates_format=yaml"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "multipart/form-data")
        decoder = MultipartDecoder(response.get_data(), response.content_type)
        (image_part, coordinates_part) = decoder.parts
        self.assertEqual(image_part.headers.get(b"Content-Type").decode(), "image/png")
        self.assertEqual(
            coordinates_part.headers.get(b"Content-Type").decode(), "application/x-yaml"
        )
        coordinates = yaml.safe_load(coordinates_part.text)
        self.assertIn("mecn0001", coordinates)

    def test_draw_get_infrastructure_parameters(self):
        response = self.client.get(
            f"/v{get_version()}/draw/infrastructure/mercury.png?"
            "parameters.margin.left=10&parameters.margin.top=10"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_draw_post_infrastructure_parameters(self):
        drawing_parameters = {"margin": {"left": 10, "top": 10}}
        response = self.client.post(
            f"/v{get_version()}/draw/infrastructure/mercury.png",
            data=json.dumps(drawing_parameters),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_draw_post_infrastructure_parameters_yaml(self):
        drawing_parameters = {"margin": {"left": 10, "top": 10}}
        response = self.client.post(
            f"/v{get_version()}/draw/infrastructure/mercury.png",
            data=yaml.dump(drawing_parameters),
            content_type="application/x-yaml",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_draw_post_infrastructure_axonometric(self):
        drawing_parameters = {"axonometric": {"enabled": True}}
        response = self.client.post(
            f"/v{get_version()}/draw/infrastructure/mercury.png",
            data=json.dumps(drawing_parameters),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_draw_get_infrastructure_invalid_parameters(self):
        response = self.client.get(
            f"/v{get_version()}/draw/infrastructure/mercury.png?parameters.fail=true"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": (
                    "Unable to load drawing parameters: Property fail is not defined "
                    "in schema for object Schema_content"
                ),
                "name": "Bad Request",
            },
        )

    def test_draw_post_infrastructure_invalid_parameters(self):
        drawing_parameters = {"fail": True}
        response = self.client.post(
            f"/v{get_version()}/draw/infrastructure/mercury.png",
            data=json.dumps(drawing_parameters),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": (
                    "Unable to load drawing parameters: Property fail is not defined "
                    "in schema for object Schema_content"
                ),
                "name": "Bad Request",
            },
        )

    def test_draw_post_infrastructure_parameters_invalid_format(self):
        response = self.client.post(
            f"/v{get_version()}/draw/infrastructure/mercury.png",
            data="fail",
            content_type="text/html",
        )
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 415,
                "description": "Unsupported request body format",
                "name": "Unsupported Media Type",
            },
        )

    def test_draw_post_infrastructure_ignored_query_parameters(self):
        response = self.client.post(
            f"/v{get_version()}/draw/infrastructure/mercury.png?parameters.fail=true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_invalid_entity(self, verb):
        response = self.client_method(verb)(f"/v{get_version()}/draw/fail/noisy.png")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": "Unable to draw entity fail",
                "name": "Bad Request",
            },
        )

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_invalid_format(self, verb):
        response = self.client_method(verb)(f"/v{get_version()}/draw/room/noisy.fail")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": "Unsupported image format fail",
                "name": "Bad Request",
            },
        )

    @parameterized.parameterized.expand([("get"), ("post")])
    def test_draw_coordinates_invalid_format(self, verb):
        response = self.client_method(verb)(
            f"/v{get_version()}/draw/room/noisy.png?coordinates&coordinates_format=fail"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json,
            {
                "code": 400,
                "description": "Unsupported coordinates format",
                "name": "Bad Request",
            },
        )

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
