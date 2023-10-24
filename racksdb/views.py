# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .generic.views import (
    DBViewSet,
    DBView,
    DBViewFilter,
    DBViewParameter,
    DBAction,
    DBActionParameter,
    DBActionResponse,
)


class RacksDBViews(DBViewSet):
    VIEWS = [
        DBView(
            content="datacenters",
            objects_name="Datacenter",
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
                "RacksDBRacksRow": "name",
                "RacksDBRack": "name",
                "RacksDBRack.nodes": None,
            },
        ),
        DBView(
            content="infrastructures",
            objects_name="Infrastructure",
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
                "RacksDBRack": "name",
                "RacksDBInfrastructure": None,
            },
        ),
        DBView(
            content="nodes",
            objects_name="Node",
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
                "RacksDBRacksRow": "name",
                "RacksDBInfrastructure": "name",
                "RacksDBRack.nodes": None,
            },
        ),
        DBView(
            content="racks",
            objects_name="Rack",
            description="Get information about racks",
            filters=[DBViewFilter(name="name", description="Filter racks by name")],
            objects_map={
                "RacksDBDatacenter": "name",
                "RacksDBDatacenterRoom": "name",
                "RacksDBRacksRow": "name",
                "RacksDBRack": None,
                "RacksDBNodeType": "id",
                "RacksDBInfrastructure": "name",
            },
        ),
    ]
    PARAMETERS = [
        DBViewParameter(
            "list",
            "Get list of object names instead of full objects",
            short="l",
            nargs=0,
        ),
        DBViewParameter("fold", "Fold expandable objects", short="f", nargs=0),
        DBViewParameter(
            "with_objects_types", "Report object types in YAML dumps", nargs=0
        ),
        DBViewParameter(
            "format",
            "Select output format",
            choices=["yaml", "json"],
        ),
    ]
    ACTIONS = [
        DBAction(
            name="draw",
            path="/draw/<entity>/<name>.<format>",
            description="Draw an entity",
            parameters=[
                DBActionParameter(
                    "entity",
                    description="Type of entity to draw",
                    choices=["infrastructure", "room"],
                    positional=True,
                ),
                DBActionParameter("name", description="Name of entity", required=True),
                DBActionParameter(
                    "format",
                    description="Format of the generated image",
                    choices=["png", "svg", "pdf"],
                    default="png",
                ),
            ],
            responses=[
                DBActionResponse("image/png", binary=True),
                DBActionResponse("image/svg+xml"),
                DBActionResponse("application/pdf", binary=True),
            ],
        )
    ]
