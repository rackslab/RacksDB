# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List, Dict, Union
from itertools import chain

from .errors import DBViewError


class DBActionParameter:
    def __init__(
        self,
        name,
        description,
        short=None,
        nargs=None,
        positional=False,
        required=False,
        choices=None,
        default=None,
        _type=None,
        body=None,
    ):
        self.name = name
        self.description = description
        self.short = short
        self.nargs = nargs
        self.positional = positional
        self.required = required
        self.choices = choices
        self.default = default
        self.type = _type
        self.body = body


class DBActionResponse:
    def __init__(self, mimetype, binary=False, object_name=None):
        self.mimetype = mimetype
        self.binary = binary
        self.object = object_name


class DBAction:
    def __init__(
        self, name, path, description, method="get", parameters=[], responses=[]
    ):
        self.name = name
        self.path = path
        self.description = description
        self.method = method
        self.parameters = parameters
        self.responses = responses

    def inpath(self, parameter: DBActionParameter) -> bool:
        """Return True if a DBActionParameter is in DBAction path"""
        return f"<{parameter.name}>" in self.path


class DBViewParameter(DBActionParameter):
    def __init__(
        self, name, description, short=None, nargs=None, choices=None, default=None
    ):
        super().__init__(
            name,
            description,
            short=short,
            nargs=nargs,
            choices=choices,
            default=default,
        )


class DBViewFilter(DBActionParameter):
    def __init__(
        self, name: str, description: str, nargs: Union[str, int, None] = None
    ):
        super().__init__(name, description, nargs=nargs)


class DBView:
    def __init__(
        self,
        content: str,
        objects_name: str,
        description: str,
        filters: List[DBViewFilter],
        objects_map: Dict[str, Union[None, str]],
    ):
        self.content = content
        self.objects_name = objects_name
        self.description = description
        self.filters = filters
        self.objects_map = objects_map


class DBViewSet:
    def __iter__(self):
        for view in self.VIEWS:
            yield view

    def views_actions(self):
        """Generate the list of generic DBActions (with their DBActionParameters and
        DBActionResponses) corresponding to the list of DBViews attached this
        DBViewSet."""
        actions = []
        for view in self:
            # Merge view filters and generic parameters to form the full list of
            # parameters.
            parameters = [
                parameter for parameter in chain(view.filters, self.parameters())
            ]
            if not len(parameters):
                parameters = None
            # List of responses
            responses = []
            for mimetype in ["application/json", "application/x-yaml"]:
                responses.append(
                    DBActionResponse(mimetype, object_name=view.objects_name)
                )
            actions.append(
                DBAction(
                    name=view.content,
                    path=f"/{view.content}",
                    description=view.description,
                    parameters=parameters,
                    responses=responses,
                )
            )
        return actions

    def parameters(self):
        for parameter in self.PARAMETERS:
            yield parameter

    def actions(self):
        for action in self.ACTIONS:
            yield action

    def __getitem__(self, key):
        for view in self.VIEWS:
            if view.content == key:
                return view
        raise DBViewError(f"Unable to find view for '{key}' content")
