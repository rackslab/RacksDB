# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from itertools import chain
from typing import Tuple, Any

from .schema import (
    SchemaObject,
    SchemaContainerList,
    SchemaBackReference,
    SchemaExpandable,
    SchemaRangeId,
    SchemaReference,
)
from .definedtype import SchemaDefinedType
from .errors import DBOpenAPIGeneratorError
from ..version import get_version


class OpenAPIGenerator:
    def __init__(self, prefix, version, schemas, views):
        self.prefix = prefix
        self.version = version
        self.schemas = schemas
        self.views = views

    def generate(self):
        """Generate an OpenAPI schema of a GenericDB and its DBViews."""
        result = {
            "openapi": "3.0.0",
            "info": {"title": f"{self.prefix} REST API", "version": get_version()},
            "paths": {},
        }

        # actions including views
        for action in chain(self.views.views_actions(), self.views.actions()):
            path = f"/v{self.version}{action.path}"
            result["paths"][path] = {action.method: {"description": action.description}}
            action_schema = result["paths"][path][action.method]
            if len(action.parameters):
                action_schema["parameters"] = []
            for parameter in action.parameters:
                if parameter.specific is not None and parameter.specific != "web":
                    continue
                if parameter.body:
                    action_schema["requestBody"] = {
                        "description": parameter.description,
                        "content": {
                            mimetype: {
                                "schema": {
                                    "$ref": f"#/components/schemas/{parameter.body}",
                                }
                            }
                            for mimetype in [
                                "application/json",
                                "application/x-yaml",
                            ]
                        },
                    }
                else:
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
            # add actions errors reponses
            for error in action.errors:
                action_schema["responses"].update(self._error_response(error))

        # components
        result["components"] = {"schemas": {}}
        for schema in self.schemas.keys():
            for _type in list(self.schemas[schema].objects.values()) + [
                self.schemas[schema].content
            ]:
                result["components"]["schemas"][f"{schema}{_type.name}"] = (
                    self._object_schema(schema, _type)
                )

        # add error component
        result["components"]["schemas"].update(self._error_component())

        return result

    def _error_component(self):
        """Return the OpenAPI component schema of a generic Error object."""
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "code": {
                        "description": "HTTP error code",
                        "type": "integer",
                        "example": 500,
                    },
                    "error": {
                        "description": "HTTP error name",
                        "type": "string",
                        "example": "Internal error",
                    },
                    "description": {
                        "description": "Detailed error description",
                        "type": "string",
                        "example": "Error while parsing object",
                    },
                },
            }
        }

    def _error_response(self, error):
        """Return the OpenAPI reponse description of a DBActionError."""
        return {
            str(error.code): {
                "description": error.description,
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/Error",
                        }
                    }
                },
            }
        }

    def _action_argument_description(self, action, parameter):
        """Return the OpenAPI description of a DBActionParameter."""
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

    def _object_schema(self, schema, _type):
        """Return the OpenAPI schema corresponding to an object."""
        result = {
            "type": "object",
            "properties": {},
        }
        if _type.description is not None:
            result["description"] = _type.description
        for prop in _type.properties:
            result["properties"][prop.name] = self._property_schema(schema, prop)
        return result

    def _property_example(self, prop):
        """Return property example. If the property is a defined type, the example value
        in schema is parsed with the defined type. If the property is not defined with
        an example in schema, it checks whether the property a reference or a back
        reference and tries to retrieve the example value on this referenced
        property."""
        # If the property does not have an example but a default value, use this default
        # value as an example.
        if prop.example is None and prop.default is not None:
            example = prop.default
        else:
            example = prop.example
        if example is not None:
            if isinstance(prop.type, SchemaDefinedType):
                return prop.type.parse(example)
            else:
                return example
        else:
            if isinstance(prop.type, SchemaReference):
                return self._property_example(prop.type.obj.prop(prop.type.prop))
            elif (
                isinstance(prop.type, SchemaBackReference)
                and prop.type.prop is not None
            ):
                return self._property_example(prop.type.obj.prop(prop.type.prop))
        return None

    def _native_type(self, native_type):
        """Convert native property type into OpenAPI type."""
        if native_type is str:
            return "string"
        elif native_type is int:
            return "integer"
        elif native_type is float:
            return "number"
        elif native_type is bool:
            return "boolean"
        raise DBOpenAPIGeneratorError(
            f"Unsupported type conversion for native type '{native_type}'"
        )

    def _native_schema(self, property_type):
        """Convert native property type into OpenAPI schema."""
        try:
            return {"type": self._native_type(property_type)}
        except DBOpenAPIGeneratorError:
            pass
        if isinstance(property_type, type(Tuple[Any, ...])):
            return {
                "type": "array",
                "items": self._native_type(property_type.__args__[0]),
            }
        raise DBOpenAPIGeneratorError(
            f"Unsupported schema conversion for property native type '{property_type}'"
        )

    def _property_schema(self, schema, prop):
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
                    "$ref": f"#/components/schemas/{schema}{prop.type.name}",
                }
            )
        elif isinstance(prop.type, SchemaExpandable):
            result.update({"type": "string"})
        elif isinstance(prop.type, SchemaRangeId):
            result.update({"type": "integer"})
        elif isinstance(prop.type, SchemaBackReference):
            if prop.type.prop is None:
                result.update(
                    {"$ref": f"#/components/schemas/{schema}{prop.type.obj.name}"}
                )
            else:
                result.update(
                    self._property_schema(schema, prop.type.obj.prop(prop.type.prop))
                )
        elif isinstance(prop.type, SchemaReference):
            result.update(
                self._property_schema(schema, prop.type.obj.prop(prop.type.prop))
            )
        elif isinstance(prop.type, SchemaContainerList):
            if isinstance(prop.type.content, SchemaObject):
                content = {
                    "$ref": f"#/components/schemas/{schema}{prop.type.content.name}"
                }
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
