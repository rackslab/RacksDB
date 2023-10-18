# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from itertools import chain

from .schema import (
    SchemaObject,
    SchemaContainerList,
    SchemaBackReference,
    SchemaExpandable,
    SchemaRangeId,
    SchemaReference,
)
from .db import DBDict, DBList
from .definedtype import SchemaDefinedType
from .errors import DBOpenAPIGenerationError
from ..version import get_version


class OpenAPIGenerator:
    def __init__(self, db, views):
        self.db = db
        self.views = views

    def generate(self):
        """Generate an OpenAPI schema of a GenericDB and its DBViews."""
        result = {
            "openapi": "3.0.0",
            "info": {"title": f"{self.db.PREFIX} REST API", "version": get_version()},
            "paths": {},
        }

        # actions including views
        for action in chain(self.views.views_actions(), self.views.actions()):
            result["paths"][action.path] = {"get": {"description": action.description}}
            action_schema = result["paths"][action.path]["get"]
            if len(action.parameters):
                action_schema["parameters"] = []
            for parameter in action.parameters:
                action_schema["parameters"].append(
                    self._action_argument_description(action, parameter)
                )
            action_schema["responses"] = {
                "200": {"description": "successful operation", "content": {}}
            }
            for response in action.responses:
                action_schema["responses"]["200"]["content"].update(
                    self._action_reponse_description(response)
                )

        # components
        result["components"] = {"schemas": {}}
        for _type in self.db._schema.objects.values():
            result["components"]["schemas"][_type.name] = self._object_schema(_type)

        return result

    def _action_argument_description(self, action, parameter):
        """Return the OpenAPI description of a DBActionArgument."""
        result = {
            "name": parameter.name,
            "in": "path" if action.inpath(parameter) else "query",
            "description": parameter.description,
            "required": parameter.required or action.inpath(parameter),
        }
        if parameter.nargs == 0:
            result.update({"schema": {}, "allowEmptyValue": True})
        elif parameter.nargs == "*":
            result.update(
                {
                    "schema": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "style": "form",
                    "explode": False,
                }
            )
        else:
            result.update(
                {
                    "schema": {
                        "type": "string",
                    }
                }
            )
        if parameter.default is not None:
            result["schema"].update({"default": parameter.default})
        if parameter.choices is not None:
            result["schema"].update({"enum": parameter.choices})
        return result

    def _action_reponse_description(self, response):
        """Return the OpenAPI description of a DBActionResponse with its content."""
        if response.binary:
            return {
                response.mimetype: {"schema": {"type": "string", "format": "binary"}}
            }
        elif response.object is not None:
            return {
                response.mimetype: {
                    "schema": {
                        "type": "array",
                        "items": {"$ref": f"#/components/schemas/{response.object}"},
                    }
                }
            }
        else:
            return {response.mimetype: {"schema": {"type": "string"}}}

    def _object_schema(self, _type):
        """Return the OpenAPI schema corresponding to an object."""
        result = {
            "type": "object",
            "properties": {},
        }
        if _type.description is not None:
            result["description"] = _type.description
        for prop in _type.properties:
            result["properties"][prop.name] = self._property_schema(prop)
        return result

    def _property_example(self, prop):
        """Return property example. If the property is a defined type, the example value
        in schema is parsed with the defined type. If the property is not defined with
        an example in schema, it checks whether the property a reference or a back
        reference and tries to retrieve the example value on this referenced
        property."""
        if prop.example is not None:
            if isinstance(prop.type, SchemaDefinedType):
                return prop.type.parse(prop.example)
            else:
                return prop.example
        else:
            if isinstance(prop.type, SchemaReference):
                return self._property_example(prop.type.obj.prop(prop.type.prop))
            elif (
                isinstance(prop.type, SchemaBackReference)
                and prop.type.prop is not None
            ):
                return self._property_example(prop.type.obj.prop(prop.type.prop))
        return None

    def _native_schema(self, property_type):
        """Convert native type into OpenAPI schema."""
        if property_type is str:
            return {"type": "string"}
        elif property_type is int:
            return {"type": "integer"}
        elif property_type is float:
            return {"type": "number"}
        elif property_type is bool:
            return {"type": "boolean"}

    def _property_schema(self, prop):
        """Return the OpenAPI schema of an object property, depending on its type."""
        result = {}
        # description
        result["description"] = prop.description
        # example if defined
        example = self._property_example(prop)
        if example is not None:
            result["example"] = example

        # schema depending on property type
        if isinstance(prop.type, SchemaObject):
            result.update(
                {
                    "$ref": f"#/components/schemas/{prop.type.name}",
                }
            )
        elif isinstance(prop.type, SchemaExpandable):
            result.update({"type": "string"})
        elif isinstance(prop.type, SchemaRangeId):
            result.update({"type": "integer"})
        elif isinstance(prop.type, SchemaBackReference):
            if prop.type.prop is None:
                result.update({"$ref": f"#/components/schemas/{prop.type.obj.name}"})
            else:
                result.update(self._property_schema(prop.type.obj.prop(prop.type.prop)))
        elif isinstance(prop.type, SchemaReference):
            result.update(self._property_schema(prop.type.obj.prop(prop.type.prop)))
        elif isinstance(prop.type, SchemaContainerList):
            if isinstance(prop.type.content, SchemaObject):
                content = {"$ref": f"#/components/schemas/{prop.type.content.name}"}
            else:
                content = self._native_schema(prop.type.content.native)
            result.update(
                {
                    "type": "array",
                    "items": content,
                }
            )
        elif isinstance(prop.type, SchemaDefinedType):
            result.update(self._native_schema(prop.type.native))
        else:
            result.update(self._native_schema(prop.type.native))
        return result
