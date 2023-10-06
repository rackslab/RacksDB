# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .generic.views import DBViewSet, DBView, DBViewFilter


class RacksDBViews(DBViewSet):
    VIEWS = [
        DBView(
            content="datacenters",
            description="Get information about datacenters",
            filters=[
                DBViewFilter(name="name", description="Filter datacenters by name"),
                DBViewFilter(
                    name="tags", description="Filter datacenters by tag", nargs="*"
                ),
            ],
            objects_map={
                "RacksDBDatacenter": None,
                "RacksDBDatacenterRoom": "name",
                "RacksDBDatacenterRoomRow": "name",
                "RacksDBDatacenterRoomRack": "name",
                "RacksDBDatacenterRoomRack.nodes": None,
            },
        ),
        DBView(
            content="infrastructures",
            description="Get information about infrastructures",
            filters=[
                DBViewFilter(name="name", description="Filter infrastructures by name"),
                DBViewFilter(
                    name="tags",
                    description="Filter infrastructures by tag",
                    nargs="*",
                ),
            ],
            objects_map={
                "RacksDBDatacenter": "name",
                "RacksDBDatacenterRoom": "name",
                "RacksDBDatacenterRoomRack": "name",
                "RacksDBInfrastructure": None,
            },
        ),
        DBView(
            content="nodes",
            description="Get information about nodes",
            filters=[
                DBViewFilter(name="name", description="Filter nodes by name"),
                DBViewFilter(
                    name="infrastructure",
                    description="Filter nodes by infrastructure",
                ),
                DBViewFilter(name="tags", description="Filter nodes by tag", nargs="*"),
            ],
            objects_map={
                "RacksDBGroupRack": "name",
                "RacksDBDatacenter": "name",
                "RacksDBDatacenterRoom": "name",
                "RacksDBDatacenterRoomRow": "name",
                "RacksDBInfrastructure": "name",
                "RacksDBDatacenterRoomRack.nodes": None,
            },
        ),
        DBView(
            content="racks",
            description="Get information about racks",
            filters=[DBViewFilter(name="name", description="Filter racks by name")],
            objects_map={
                "RacksDBDatacenter": "name",
                "RacksDBDatacenterRoom": "name",
                "RacksDBDatacenterRoomRow": "name",
                "RacksDBDatacenterRoomRack": None,
                "RacksDBNodeType": "id",
                "RacksDBInfrastructure": "name",
            },
        ),
    ]
