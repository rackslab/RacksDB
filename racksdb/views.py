# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

from .drawers.parameters import DrawingParameters
from .generic.views import (
    DBViewSet,
    DBView,
    DBViewFilter,
    DBViewParameter,
    DBAction,
    DBActionParameter,
    DBActionResponse,
    DBActionError,
)


class RacksDBViews(DBViewSet):
    VIEWS = [
        DBView(
            content="datacenters",
            objects_name="RacksDBDatacenter",
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
            objects_name="RacksDBInfrastructure",
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
            objects_name="RacksDBNode",
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
            objects_name="RacksDBRack",
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
            method="post",
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
                DBActionParameter(
                    "parameters",
                    description="Drawing parameters",
                    body="Drawings_content",
                ),
                DBActionParameter(
                    "drawings_schema",
                    description="Schema of drawing parameters",
                    _type=Path,
                    default=DrawingParameters.DEFAULT_SCHEMA,
                    specific="cli",
                ),
                DBActionParameter(
                    "coordinates",
                    description=(
                        "Dump equipments and racks coordinates in diagrams (default: "
                        "disabled, default filename: coordinates.<FORMAT>)"
                    ),
                    short="c",
                    nargs="?",
                    _type=Path,
                    default=False,
                    default_in_help=False,
                    const=True,
                    specific="cli",
                ),
                DBActionParameter(
                    "coordinates_format",
                    description="Format of coordinates",
                    choices=["json", "yaml"],
                    default="json",
                ),
            ],
            responses=[
                DBActionResponse("image/png", binary=True),
                DBActionResponse("image/svg+xml"),
                DBActionResponse("application/pdf", binary=True),
            ],
            errors=[
                DBActionError(400, "Unable to parse drawing parameters in JSON format"),
                DBActionError(
                    415,
                    "Unsupported drawing parameters format or unable to load drawing "
                    "parameters schema",
                ),
            ],
        )
    ]
