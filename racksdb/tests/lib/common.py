# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from pathlib import Path

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def _first_path(paths, error):
    for path in paths:
        if path.exists():
            return path
    raise FileNotFoundError(error)


def drawing_schema_path():
    return _first_path(
        [
            Path(CURRENT_DIR).joinpath("../../../schemas/drawings.yml"),
            Path("/usr/share/racksdb/schemas/drawings.yml"),
        ],
        "Unable to find drawing schema to run tests",
    )


def schema_path():
    return _first_path(
        [
            Path(CURRENT_DIR).joinpath("../../../schemas/racksdb.yml"),
            Path("/usr/share/racksdb/schemas/racksdb.yml"),
        ],
        "Unable to find schema to run tests",
    )


def db_path():
    return _first_path(
        [
            Path(CURRENT_DIR).joinpath("../../../examples/db"),
            Path("/usr/share/doc/racksdb/examples/db"),
        ],
        "Unable to find database to run tests",
    )


def db_one_file_path():
    return Path(CURRENT_DIR).joinpath("../../../examples/simple/racksdb.yml")


def ui_path():
    # This path does not contain the full UI application but enough files to
    # test.
    return _first_path(
        [Path(CURRENT_DIR).joinpath("../../../frontend/public")],
        "Unable to find UI public directory to run tests",
    )
