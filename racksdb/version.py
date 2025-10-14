# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

try:
    from importlib import metadata
except ImportError:
    # On Python < 3.8, use external backport library importlib-metadata.
    import importlib_metadata as metadata


def get_version():
    return metadata.version("racksdb")
