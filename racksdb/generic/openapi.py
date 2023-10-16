# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

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

        for view in self.views:
            result["paths"][f"/{view.content}"] = {
                "get": {"description": view.description}
            }
            view_path = result["paths"][f"/{view.content}"]["get"]
            if len(view.filters):
                view_path["parameters"] = []

            for _filter in view.filters:
                view_path["parameters"].append(
                    self._filter_parameter_description(_filter)
                )
                view_path["responses"] = self._view_response(view.content)

            # generic view parameters
            for parameter in self.views.parameters():
                view_path["parameters"].append(
                    self._generic_parameter_description(parameter)
                )

        # components
        result["components"] = {"schemas": {}}
        for _type in self.db._schema.objects.values():
            result["components"]["schemas"][_type.name] = self._object_schema(_type)

        return result

    def _filter_parameter_description(self, _filter):
        """Return the OpenAPI description of a DBView filter."""
        result = {
            "name": _filter.name,
            "in": "query",
            "description": _filter.description,
            "required": False,
        }
        if _filter.nargs == "*":
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
        return result

    def _generic_parameter_description(self, parameter):
        """Return the OpenAPI description of a DBViews generic parameter."""
        result = {
            "name": parameter.name,
            "in": "query",
            "description": parameter.description,
            "required": False,
        }
        if parameter.type is None:
            result.update({"schema": {}, "allowEmptyValue": True})
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

    def _view_response(self, content):
        """Return the OpenAPI response description of a DBView and its content."""
        view_content = getattr(self.db, content)
        # select 1st object returned in view to get its type
        if isinstance(view_content, DBList):
            view_object_type = view_content[0]._schema.name
        elif isinstance(view_content, DBDict):
            view_object_type = view_content.first()._schema.name
        return {
            "200": {
                "description": "successful operation",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": f"#/components/schemas/{view_object_type}"
                            },
                        }
                    },
                    "application/x-yaml": {
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": f"#/components/schemas/{view_object_type}"
                            },
                        }
                    },
                },
            }
        }

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
