# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import typing as t

from racksdb.generic.views import (
    DBViewSet,
    DBView,
    DBViewParameter,
    DBViewFilter,
    DBAction,
    DBActionParameter,
    DBActionResponse,
    DBActionError,
)


class TestDBViews(DBViewSet):
    VIEWS = [
        DBView(
            content="apples",
            objects_name="TestDBApple",
            description="Get information about apples",
            filters=[
                DBViewFilter(name="name", description="Filter apples by name"),
                DBViewFilter(
                    name="color", description="Filter apples by color", nargs="*"
                ),
            ],
            objects_map={},
        ),
    ]
    PARAMETERS = [
        DBViewParameter(
            "format",
            "Select output format",
            choices=["yaml", "json"],
        ),
    ]
    ACTIONS = [
        DBAction(
            name="sell",
            path="/sell",
            description="Sell fruits",
            methods=["GET", "POST"],
            parameters=[
                DBActionParameter(
                    "type", description="Type of fruits", default="apple"
                ),
                DBActionParameter(
                    "negotiable",
                    description="Can price be negociated?",
                    nargs=0,
                ),
                DBActionParameter(
                    "buyer",
                    description="Name of buyer",
                    specific="cli",
                ),
                DBActionParameter(
                    "parameters",
                    description="Sales parameters",
                    schema="Test",
                    in_body=True,
                ),
            ],
            responses=[
                DBActionResponse("application/json", schema=int),
                DBActionResponse("application/x-yaml", schema=t.List[str]),
            ],
            errors=[
                DBActionError(
                    400,
                    "Missing request parameter.",
                ),
                DBActionError(
                    404,
                    "Type of fruits not found in database.",
                ),
            ],
        ),
    ]
