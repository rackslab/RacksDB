# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import copy

from racksdb.generic.db import DBDictsLoader, GenericDB, DBDict
from racksdb.generic.errors import DBFormatError

from .lib.common import valid_schema, VALID_DB
from .lib import bases


class TestGenericDB(unittest.TestCase):
    def setUp(self):
        self.db = GenericDB("Test", valid_schema(), bases)

    def test_load(self):
        loader = DBDictsLoader(VALID_DB)
        self.db.load(loader)
        self.assertIsInstance(self.db.apples, DBDict)
        self.assertEqual(self.db.apples.first().__class__.__name__, "TestApple")

    def test_not_unique_key(self):
        content = copy.deepcopy(VALID_DB)
        content["apples"].append(
            {"name": "golden", "color": "fail", "weight": "50g"},
        )
        loader = DBDictsLoader(content)
        with self.assertRaisesRegex(
            DBFormatError, "Key value golden of SchemaApple is not unique"
        ):
            self.db.load(loader)

    def test_missing_property(self):
        content = copy.deepcopy(VALID_DB)
        del content["pear"]
        loader = DBDictsLoader(content)
        with self.assertRaisesRegex(
            DBFormatError,
            "Property pear is required in schema for object Schema_content",
        ):
            self.db.load(loader)

    def test_invalid_valid(self):
        content = copy.deepcopy(VALID_DB)
        content["pear"]["color"] = 0
        loader = DBDictsLoader(content)
        with self.assertRaisesRegex(DBFormatError, "color 0 is not a valid str"):
            self.db.load(loader)

    def test_invalid_list(self):
        content = copy.deepcopy(VALID_DB)
        content["bananas"] = "fail"
        loader = DBDictsLoader(content)
        with self.assertRaisesRegex(
            DBFormatError, r"token bananas list\[SchemaBananaOrigin\] must be a list"
        ):
            self.db.load(loader)

    def test_invalid_property(self):
        content = copy.deepcopy(VALID_DB)
        content["pear"]["fail"] = "fail"
        loader = DBDictsLoader(content)
        with self.assertRaisesRegex(
            DBFormatError,
            "Property fail is not defined in schema for object SchemaPear",
        ):
            self.db.load(loader)

    def test_invalid_defined_type(self):
        content = copy.deepcopy(VALID_DB)
        content["pear"]["weight"] = "fail"
        loader = DBDictsLoader(content)
        with self.assertRaisesRegex(
            DBFormatError,
            "Unable to match ~racksdb.tests.generic.lib.common pattern with value fail",
        ):
            self.db.load(loader)

    def test_invalid_reference(self):
        content = copy.deepcopy(VALID_DB)
        content["stock"]["content"][0]["species"] = "fail"
        loader = DBDictsLoader(content)
        with self.assertRaisesRegex(
            DBFormatError,
            "Unable to find species reference with value fail",
        ):
            self.db.load(loader)

    def test_defined_backref(self):
        content = copy.deepcopy(VALID_DB)
        content["bananas"][0]["species"]["cavendish"]["origin"] = "france"
        loader = DBDictsLoader(content)
        with self.assertRaisesRegex(
            DBFormatError,
            r"Back reference origin cannot be defined in database for object "
            r"\^SchemaBananaOrigin",
        ):
            self.db.load(loader)

    def test_defined_computed(self):
        content = copy.deepcopy(VALID_DB)
        content["stock"]["total"] = 0
        loader = DBDictsLoader(content)
        with self.assertRaisesRegex(
            DBFormatError,
            "AppleStock>total is a computed property, thus it cannot be defined in "
            "database.",
        ):
            self.db.load(loader)

    def test_invalid_expandable_type(self):
        modified_db = copy.deepcopy(VALID_DB)
        modified_db["stock"]["content"][0]["name"] = 1
        loader = DBDictsLoader(modified_db)
        # FIXME: error message is grammatically wrong
        with self.assertRaisesRegex(
            DBFormatError, "token name of expandable is not a valid expandable str"
        ):
            self.db.load(loader)

    def test_invalid_expandable_range(self):
        modified_db = copy.deepcopy(VALID_DB)
        modified_db["stock"]["content"][0]["name"] = "create[10-01]"
        _ = DBDictsLoader(modified_db)
        # FIXME: should raise DBFormatError instead of
        # ClusterShell.NodeSet.NodeSetParseRangeError
        # self.db.load(loader)
