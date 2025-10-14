# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import unittest

# Expected values from testing reference DB.
REFDB_DATACENTERS = ["paris", "london"]
REFDB_INFRASTRUCTURES = ["mercury", "jupiter", "sharednet"]
REFDB_TOTAL_NODES = 130


class TestRacksDBReferenceDB(unittest.TestCase):
    """Abstract TestCase class with method to validate data from testing reference
    database."""

    def assertDatacentersResponse(self, content):
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 2)
        self.assertCountEqual(
            [datacenter["name"] for datacenter in content], REFDB_DATACENTERS
        )
        self.assertIsInstance(content[0], dict)
        # tags key is optional, it may not be present in selected datacenter.
        for key in ["name", "rooms", "location"]:
            self.assertIn(
                key,
                content[0],
            )

    def assertInfrastructuresResponse(self, content):
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 3)
        self.assertCountEqual(
            [infrastructure["name"] for infrastructure in content],
            REFDB_INFRASTRUCTURES,
        )
        self.assertIsInstance(content[0], dict)
        # tags key is optional, it may not be present in selected infrastructure.
        for key in ["name", "description", "layout"]:
            self.assertIn(
                key,
                content[0],
            )

    def assertNodesResponse(self, content):
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 130)
        self.assertIsInstance(content[0], dict)
        self.assertCountEqual(
            content[0].keys(),
            ["name", "infrastructure", "rack", "type", "slot", "tags", "position"],
        )

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
