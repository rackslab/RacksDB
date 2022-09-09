#!/usr/bin/env python3
#
# Copyright (C) 2022 Rackslab
#
# This file is part of RacksDB.
#
# RacksDB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RacksDB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RacksDB.  If not, see <https://www.gnu.org/licenses/>.

from typing import List, Dict, Union, Optional


class RacksDBNodeTypeCPU:
    def __init__(self, sockets: int, model: str, specs: str, cores: int):
        pass


class RacksDBNodeTypeRAM:
    def __init__(self, dimm: int, size: int):
        pass


class RacksDBNodeTypeNetif:
    def __init__(self, type: str, bandwidth: int):
        pass


class RacksDBNodeTypeStorage:
    def __init__(self, type: str, model: str, size: int):
        pass


class RacksDBNodeType:
    def __init__(
        self,
        id: str,
        model: str,
        height: float,
        width: float,
        specs: Optional[str],
        cpus: RacksDBNodeTypeCPU,
        ram: RacksDBNodeTypeRAM,
        netifs: List[RacksDBNodeTypeNetif],
        storage: List[RacksDBNodeTypeNetif],
    ):
        pass

    @classmethod
    def load(cls, nodetype: Dict[str, Union[str, Dict, List]]):
        return cls(
            nodetype['id'],
            nodetype['model'],
            nodetype['height'],
            nodetype['width'],
            nodetype['specs'],
            nodetype['cpus'],
            nodetype['ram'],
            nodetype['netifs'],
            nodetype['storage'],
        )
