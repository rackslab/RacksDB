# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest import mock
import io

import werkzeug

from racksdb.web.app import RacksDBWebApp

from ..lib.web import RacksDBCustomTestResponse
from ..lib.common import schema_path, db_path, ui_path

CMD_BASE_ARGS = [
    "--schema",
    str(schema_path()),
    "--db",
    str(db_path()),
]


class TestRacksDBWebApp(unittest.TestCase):
    def test_init(self):
        RacksDBWebApp(CMD_BASE_ARGS)

    def test_init_with_ui(self):
        RacksDBWebApp(CMD_BASE_ARGS + ["--with-ui"])

    def test_init_with_cors(self):
        RacksDBWebApp(CMD_BASE_ARGS + ["--cors"])

    def test_schema_not_found(self):
        args = CMD_BASE_ARGS.copy()
        args[1] = "/dev/fail"
        with mock.patch("sys.stderr", new=io.StringIO()) as errors:
            with self.assertRaisesRegex(SystemExit, "1"):
                RacksDBWebApp(args)
        self.assertIn(
            "Error while loading schema: Schema path /dev/fail does not exist",
            errors.getvalue(),
        )

    def test_db_not_found(self):
        args = CMD_BASE_ARGS.copy()
        args[3] = "/dev/fail"
        with mock.patch("sys.stderr", new=io.StringIO()) as errors:
            with self.assertRaisesRegex(SystemExit, "1"):
                RacksDBWebApp(args)
        self.assertIn(
            "Error while loading db: DB path /dev/fail does not exist",
            errors.getvalue(),
        )


class TestRacksDBWebAppEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = RacksDBWebApp(CMD_BASE_ARGS + ["--with-ui", str(ui_path())])
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

    def test_config(self):
        response = self.client.get("/config.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIsInstance(response.json, dict)
        for key in ["API_SERVER", "API_VERSION"]:
            self.assertIn(key, response.json)

    def test_static_ui(self):
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/vnd.microsoft.icon")
