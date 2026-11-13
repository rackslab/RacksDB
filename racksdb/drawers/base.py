# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import logging

from ..generic.db import GenericDB

logger = logging.getLogger(__name__)


def default_rack_colorset(parameters):
    schema_object = parameters.colors._schema.prop("racks").type.content
    return GenericDB("DefaultsColorSet", parameters.colors._schema, None).load_object(
        "racks", schema_object.recursive_defaults(), schema_object, None
    )


def default_equipment_colorset(parameters):
    schema_object = parameters.colors._schema.prop("equipments").type.content
    return GenericDB("DefaultsColorSet", parameters.colors._schema, None).load_object(
        "equipments", schema_object.recursive_defaults(), schema_object, None
    )


class Drawer:
    """Base class of all drawers, independent of the output format."""

    def __init__(self, db, file, output_format, parameters):
        self.db = db
        self.file = file
        self.output_format = output_format
        self.parameters = parameters

    def _find_rack_colorset(self, rack):
        """Return the rack matching coloring rule defined in drawing parameters or the
        default rack color set.

        An rack coloring rule can have an rack type name and a list of tags. For a
        coloring rule to match a rack, the following conditions must be verified:

        - If the coloring rule has a type, the id of the rack type must match.
        - If the coloring rule has a list of tags, the rack must have tags and its
          tags must contain all coloring rule tags.

        In other cases, the coloring rule does not match. If no coloring rule matches
        the rack, the default rack color set is returned."""
        for rule in self.parameters.colors.racks:
            if hasattr(rule, "type") and rule.type != rack.type.id:
                continue
            if hasattr(rule, "tags") and (
                not hasattr(rack, "tags")
                or not all(tag in rack.tags for tag in rule.tags)
            ):
                continue
            return rule
        return default_rack_colorset(self.parameters)

    def _find_equipment_colorset(self, equipment):
        """Return the equipment matching coloring rule defined in drawing parameters or
        the default equipment color set.

        An equipment coloring rule can have an equipment type name and a list of
        tags. For a coloring rule to match an equipment, the following conditions
        must be verified:

        - If the coloring rule has a type, the id of the equipment type must match.
        - If the coloring rule has a list of tags, the equipment must have tags
          and its tags must contain all coloring rule tags.

        In other cases, the coloring rule does not match. If no coloring rule matches
        the equipment, the default equipment color set is returned."""
        for rule in self.parameters.colors.equipments:
            if hasattr(rule, "type") and rule.type != equipment.type.id:
                continue
            if hasattr(rule, "tags") and (
                not hasattr(equipment, "tags")
                or not all(tag in equipment.tags for tag in rule.tags)
            ):
                continue
            return rule
        return default_equipment_colorset(self.parameters)
