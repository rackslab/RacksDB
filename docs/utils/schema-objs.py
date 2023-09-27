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
  To generate partial of database objects reference documentation, run this
  command:

  $ python3 docs/utils/schema-objs.py > docs/modules/db/partials/objects.adoc
"""
from pathlib import Path

import yaml
import jinja2

from racksdb import RacksDB
from racksdb.generic.schema import SchemaBackReference


class LineLoader(yaml.loader.SafeLoader):
    """Custom loader to line number of every nodes YAML file."""

    def __init__(self, stream):
        super().__init__(stream)

    def compose_node(self, parent, index):
        # the line number where the previous token has ended (plus empty lines)
        line = self.line
        node = yaml.composer.Composer.compose_node(self, parent, index)
        node.__line__ = line
        return node

    def construct_mapping(self, node, deep=False):
        additional_pairs = []

        for key, value in node.value:
            line_key = yaml.nodes.ScalarNode(
                tag=yaml.resolver.BaseResolver.DEFAULT_SCALAR_TAG,
                value="__line_" + key.value,
            )
            line_value = yaml.nodes.ScalarNode(
                tag=yaml.resolver.BaseResolver.DEFAULT_SCALAR_TAG,
                value=key.__line__,
            )
            additional_pairs.append((line_key, line_value))

        node.value += additional_pairs
        mapping = yaml.constructor.Constructor.construct_mapping(self, node, deep=deep)
        return mapping


def bases(obj):
    """Jinja2 Filter to list of parent classes names of an object."""
    return [_class.__name__ for _class in obj.__class__.__bases__]


def main():
    # Load the schema, the DB does not matter here.
    db = RacksDB.load(
        schema=Path("../schema/racksdb.yml"),
        db=Path("../examples/simple/racksdb.yml"),
    )

    with open("../schema/racksdb.yml") as fh:
        # Load the schema with LineLoader to get line numbers of attributes
        # objects declarations
        data = yaml.load(fh.read(), Loader=LineLoader)
        # Also load schema file in memory to get individual lines content.
        fh.seek(0)
        schema_lines = fh.readlines()

    # Enrich schema with description provided in schema file, in comment in the
    # line of the property declaration.
    for obj in [db._schema.content] + list(db._schema.objects.values()):
        if obj.name != "_content":
            obj_line = schema_lines[data["_objects"]["__line_" + obj.name]]
            if "#" in obj_line:
                obj.description = obj_line.split("#", 1)[1].strip()
            else:
                obj.description = None
        for prop in obj.properties:
            if obj is db._schema.content:
                item = data["_content"]
            else:
                item = data["_objects"][obj.name]
            prop_line = schema_lines[item["__line_" + prop.name]]
            if "#" in prop_line:
                prop.description = prop_line.split("#", 1)[1].strip()
            else:
                prop.description = "-"

    # Enrich schema object with has_backref boolean
    for obj in db._schema.objects.values():
        obj.has_backref = False
        for prop in obj.properties:
            if isinstance(prop.type, SchemaBackReference):
                obj.has_backref = True

    # Render template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("utils"))
    env.filters["bases"] = bases
    template = env.get_template("schema-objs.adoc.j2")
    output = template.render(
        schema=db._schema,
        object_prefix="RacksDB",
        deftype_prefix="racksdb.dtypes.",
    )
    print(output)


if __name__ == "__main__":
    main()
