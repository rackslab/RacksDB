# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import os
import unittest
from pathlib import Path
from unittest import mock

from racksdb.env import env_or_default


class TestEnvOrDefault(unittest.TestCase):
    def test_uses_fallback_when_key_missing(self):
        key = "RACKSDB_TEST_ENV_OR_DEFAULT_MISSING"
        self.assertNotIn(key, os.environ)
        p = env_or_default(key, "/tmp/fallback")
        self.assertEqual(p, Path("/tmp/fallback"))

    def test_uses_fallback_when_empty_string(self):
        key = "RACKSDB_TEST_ENV_OR_DEFAULT_EMPTY"
        with mock.patch.dict(os.environ, {key: ""}, clear=False):
            p = env_or_default(key, "/tmp/fallback")
        self.assertEqual(p, Path("/tmp/fallback"))

    def test_uses_environment_when_set(self):
        key = "RACKSDB_TEST_ENV_OR_DEFAULT_SET"
        with mock.patch.dict(os.environ, {key: "/from/env"}, clear=False):
            p = env_or_default(key, "/tmp/fallback")
        self.assertEqual(p, Path("/from/env"))

    def test_fallback_accepts_path(self):
        key = "RACKSDB_TEST_ENV_OR_DEFAULT_PATH_FALLBACK"
        fb = Path("/tmp/fallback_path")
        with mock.patch.dict(os.environ, {key: ""}, clear=False):
            p = env_or_default(key, fb)
        self.assertEqual(p, fb)
