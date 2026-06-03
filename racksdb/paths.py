# Copyright (c) 2026 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

"""Resolve default paths for schema files shipped with RacksDB."""

import sys
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent
_SOURCE_TREE_SCHEMAS = _PACKAGE_ROOT.parent / "schemas"
_FHS_SCHEMAS_DIR = Path("/usr/share/racksdb/schemas")


def schema_file(name: str) -> Path:
    """Return the best available path for a schema *name*.

    Resolution order:

    1. Distribution FHS path /usr/share/racksdb/schemas/<name>
    2. Pip-installed data files under <prefix>/share/racksdb/schemas/<name>
    3. Source tree schemas/<name> next to the repository root (editable checkout)

    If none of the above paths exist, the distribution path is returned anyway to
    preserve documented path in error messages.
    """
    fhs = _FHS_SCHEMAS_DIR / name
    if fhs.is_file():
        return fhs

    pip_path = Path(sys.prefix) / "share" / "racksdb" / "schemas" / name
    if pip_path.is_file():
        return pip_path

    dev_path = _SOURCE_TREE_SCHEMAS / name
    if dev_path.is_file():
        return dev_path

    return fhs
