# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest import mock
import io

import werkzeug

from racksdb.web.app import RacksDBWebApp, merge_args_parameters

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
        try:
            self.app = RacksDBWebApp(CMD_BASE_ARGS + ["--with-ui", str(ui_path())])
        except FileNotFoundError as err:
            self.skipTest(err)
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


class TestMergeArgsParameters(unittest.TestCase):
    def test_merge(self):
        content = {"key1": "value1"}
        args = {"parameters.key2": "value2"}
        merge_args_parameters(content, args)
        self.assertEqual(content, {"key1": "value1", "key2": "value2"})

    def test_merge_overwrite(self):
        content = {"key1": "value1"}
        args = {"parameters.key1": "value2"}
        merge_args_parameters(content, args)
        self.assertEqual(content, {"key1": "value2"})

    def test_merge_ignored(self):
        content = {"key1": "value1"}
        args = {"ignored.key2": "value2"}
        merge_args_parameters(content, args)
        self.assertEqual(content, {"key1": "value1"})

    def test_merge_subs(self):
        content = {
            "key1": {
                "key1sub1": "value1",
                "key1sub2": "value2",
            }
        }
        args = {
            "parameters.key1.key1sub1": "value1.2",
            "parameters.key1.key1sub3": "value3",
            "parameters.key2.key2sub1": "value4",
        }
        merge_args_parameters(content, args)
        self.assertEqual(
            content,
            {
                "key1": {
                    "key1sub1": "value1.2",
                    "key1sub2": "value2",
                    "key1sub3": "value3",
                },
                "key2": {"key2sub1": "value4"},
            },
        )

    def test_merge_int(self):
        content = {"key1": 0}
        args = {"parameters.key1": "1"}
        merge_args_parameters(content, args)
        self.assertEqual(content, {"key1": 1})

    def test_merge_bool_true(self):
        content = {"key1": False}
        args = {"parameters.key1": "true"}
        merge_args_parameters(content, args)
        self.assertEqual(content, {"key1": True})

    def test_merge_list(self):
        content = {"key1": []}
        args = {"parameters.key1": "value1,value2"}
        merge_args_parameters(content, args)
        self.assertEqual(content, {"key1": ["value1", "value2"]})
