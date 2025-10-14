# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from typing import List, Dict, Optional, Union, Any
from itertools import chain

from .errors import DBViewError


class DBActionParameter:
    """Represents a parameter of a DBAction.

    Attributes:
        name: Name of the parameter.
        description: Description of the parameter. It is used as help message in CLI and
          parameter description in OpenAPI description, or as requestBody description if
          body is defined.
        short: Alternative short command line argument name to enable the parameter.
          This attribute has no effect on REST API.
        nargs: Number of values accepted by the parameter. By default, the parameter
          accepts one value. Possible alternatives are 0, "*" or "?". With 0, the value
          of the parameter is a boolean on CLI and is marked as allowEmptyValue in
          OpenAPI description. With "*" multiple values are accepted. With "?", the
          value is optional.
        positional: When True, the parameter is set as positional on the CLI. This
          attribute has no effect on REST API.
        required: When True, the corresponding command line argument is set as required
          in CLI and reported as required in OpenAPI description.
        choices: Possible accepted values for the parameter.
        default: Default value of the parameter.
        default_in_help: When True, the default value is reported in CLI help message.
          This attribute does not have any effect on REST API.
        const: Constant value used in CLI. This attribute has no effect on REST API.
        _type: Type of the value after parsing on CLI. This attribute does not have any
          effect on REST API.
        schema: Name reference to database schema provided to OpenAPI generator. The
          objects and attributes defined in this schema are expanded to request
          parameters, except for POST method when in_body is True. This attribute has no
          effect on CLI.
        in_body: When True, the reference schema is the body content of the action
          request in OpenAPI description. This attribute has no effect on CLI.
        specific: Define if this parameter is either specific to REST API or CLI.
          Possible values are "web" (ie. REST API specific) and "cli" (ie. CLI
          specific).
    """

    def __init__(
        self,
        name: str,
        description: str,
        short: Optional[str] = None,
        nargs: Optional[Union[str, int]] = None,
        positional: bool = False,
        required: bool = False,
        choices: Optional[List[str]] = None,
        default: Any = None,
        default_in_help: bool = True,
        const: Any = None,
        _type: Any = None,
        schema: Optional[str] = None,
        in_body: bool = False,
        specific: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.short = short
        self.nargs = nargs
        self.positional = positional
        self.required = required
        self.choices = choices
        self.default = default
        self.default_in_help = default_in_help
        self.const = const
        self.type = _type
        self.schema = schema
        self.in_body = in_body
        self.specific = specific


class DBActionResponse:
    def __init__(self, mimetype, binary=False, object_name=None, schema=str):
        self.mimetype = mimetype
        self.binary = binary
        self.object = object_name
        self.schema = schema


class DBActionError:
    def __init__(self, code: int, description):
        self.code = code
        self.description = description


class DBAction:
    def __init__(
        self,
        name,
        path,
        description,
        methods=["GET"],
        parameters=[],
        responses=[],
        errors=[],
    ):
        self.name = name
        self.path = path
        self.description = description
        self.methods = methods
        self.parameters = parameters
        self.responses = responses
        self.errors = errors

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
