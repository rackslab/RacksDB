# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import typing as t
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
            methods=["POST", "GET"],
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
                    schema="Drawings",
                    in_body=True,
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
                        "Dump equipments and racks coordinates in diagrams. When this "
                        "parameter is set, the mimetype of the response is "
                        "`multipart/form-data`."
                    ),
                    nargs=0,
                    specific="web",
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
                DBActionResponse("multipart/form-data", binary=True),
            ],
            errors=[
                DBActionError(
                    400,
                    "Unsupported entity, unable to load drawing parameters, "
                    "unsupported image format, unsupported coordinates format"
                    "or unable to load requested entity in database.",
                ),
                DBActionError(415, "Unsupported drawing parameters format."),
                DBActionError(500, "Unable to load drawing parameters schema."),
            ],
        ),
        DBAction(
            name="tags",
            path="/tags",
            description="Get tags associated to infrastructure and equipment",
            parameters=[
                DBActionParameter(
                    "infrastructure",
                    description="Infrastructure name",
                ),
                DBActionParameter(
                    "on-nodes",
                    nargs=0,
                    description="Get tags on nodes of an infrastructure",
                ),
                DBActionParameter(
                    "node",
                    description="Node name",
                ),
                DBActionParameter(
                    "datacenter",
                    description="Datacenter name",
                ),
                DBActionParameter(
                    "on-racks",
                    nargs=0,
                    description="Get tags of racks in a datacenter",
                ),
            ],
            responses=[
                DBActionResponse("application/json", schema=t.List[str]),
                DBActionResponse("application/x-yaml", schema=t.List[str]),
            ],
            errors=[
                DBActionError(
                    400,
                    "Missing request parameter.",
                ),
                DBActionError(
                    404,
                    "Requested objects not found in database.",
                ),
            ],
        ),
    ]
