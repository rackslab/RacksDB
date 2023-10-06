# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from ClusterShell.NodeSet import NodeSet

from ..errors import DBDumperError


class DBDumperConsole:
    def __init__(self, show_types=False, objects_map={}, fold=True):
        self.objects_map = objects_map
        self.fold = fold

    def dump(
        self,
        obj: Any,
    ) -> str:
        if not isinstance(obj, list):
            raise DBDumperError(f"Unsupported type '{type(obj)}' for DBDumperConsole")
        if self.fold:
            nodeset = NodeSet()
            for item in obj:
                nodeset.update(item)
            return str(nodeset)
        else:
            return "\n".join(obj)
