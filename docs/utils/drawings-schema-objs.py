#!/usr/bin/python3
#
# Copyright (C) 2022 Rackslab
#
# This file is part of RacksDB.
#
# RacksDB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RacksDB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RacksDB.  If not, see <https://www.gnu.org/licenses/>.

"""
  To generate partial of drawing parameters database objects reference documentation,
  run this command:

  $ python3 docs/utils/drawings-schema-objs.py > \
    modules/usage/partials/drawing-objects.adoc
"""
from pathlib import Path

import jinja2
import yaml

from racksdb.drawers.parameters import DrawingParameters
from racksdb.generic.schema import (
    Schema,
    SchemaFileLoader,
    SchemaDefinedTypeLoader,
    SchemaBackReference,
)


def bases(obj):
    """Jinja2 Filter to list of parent classes names of an object."""
    return [_class.__name__ for _class in obj.__class__.__bases__]


def toyaml(stuff):
    return yaml.dump(stuff).rstrip()


def main():
    # Load the schema, the DB does not matter here.
    drawing_schema = Schema(
        SchemaFileLoader(Path("../schema/drawings.yml")),
        SchemaDefinedTypeLoader(DrawingParameters.DEFINED_TYPES_MODULE),
    )

    # Enrich schema object with has_backref boolean
    for obj in drawing_schema.objects.values():
        obj.has_backref = False
        for prop in obj.properties:
            if isinstance(prop.type, SchemaBackReference):
                obj.has_backref = True

    # Render template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("utils"))
    env.filters["bases"] = bases
    env.filters["toyaml"] = toyaml
    template = env.get_template("schema-objs.adoc.j2")
    output = template.render(
        schema=drawing_schema,
        object_prefix="Drawings",
        deftype_prefix="racksdb.drawers.dtypes.",
    )
    print(output)


if __name__ == "__main__":
    main()
