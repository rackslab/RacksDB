# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

"""Environment variable names and helpers for RacksDB CLI entry points."""

import os
from pathlib import Path
import typing as t


class RacksDBEnv:
    SCHEMA = "RACKSDB_SCHEMA"
    EXTENSIONS = "RACKSDB_EXTENSIONS"
    DB = "RACKSDB_DB"


def env_or_default(env_key: str, fallback: t.Union[str, Path]) -> Path:
    """Path from ``os.environ[env_key]`` if set and non-empty, else *fallback*."""
    val = os.environ.get(env_key)
    if val:
        return Path(val)
    return Path(fallback)
