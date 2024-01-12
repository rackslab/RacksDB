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

import jinja2

from racksdb import RacksDB
from racksdb.generic.schema import SchemaBackReference


def bases(obj):
    """Jinja2 Filter to list of parent classes names of an object."""
    return [_class.__name__ for _class in obj.__class__.__bases__]


def main():
    # Load the schema, the DB does not matter here.
    db = RacksDB.load(
        schema=Path("../schemas/racksdb.yml"),
        db=Path("../examples/simple/racksdb.yml"),
    )

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
