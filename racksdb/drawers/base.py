# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

from itertools import chain
import logging

from ..errors import RacksDBDrawingError
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

    def _find_infrastructure(self, name):
        """Return the infrastructure with the given name. Raise RacksDBDrawingError if
        not found in database."""
        for infrastructure in self.db.infrastructures:
            if infrastructure.name == name:
                return infrastructure
        raise RacksDBDrawingError(f"Unable to find infrastructure {name} in database")

    def _equipment_selected(self, equipment) -> bool:
        """Return True if the equipment is selected for representation with the
        equipment_tags drawing parameter, ie. if this parameter is unset or if the
        equipment has at least one matching tag, False otherwise."""
        if not hasattr(self.parameters.infrastructure, "equipment_tags"):
            return True
        return any(
            equipment_tag in self.parameters.infrastructure.equipment_tags
            for equipment_tag in equipment.tags
        )

    def _part_contains_selected_equipment(self, part) -> bool:
        """Return True if the infrastructure part contains equipment that is selected
        for representation, False otherwise."""

        # If equipment_tags is unset, all equipment is represented, then it is True.
        if not hasattr(self.parameters.infrastructure, "equipment_tags"):
            return True
        # Iterate over all equipment to check if at least one has matching tag.
        for equipment in chain(part.nodes, part.storage, part.network, part.misc):
            if self._equipment_selected(equipment):
                return True
        # No matching equipment found, return False.
        return False

    def _select_infrastructure_racks(self, infrastructure):
        """Return the tuple of lists (racks, rows) of racks and racks rows of the
        infrastructure to represent according to drawing parameters. Raise
        RacksDBDrawingError if no rack is selected."""
        racks = []
        rows = []

        def add_rack(rack):
            # Racks objects are compared by names, as the same rack can be
            # represented by distinct objects.
            if all(rack.name != selected.name for selected in racks):
                racks.append(rack)

        for part in infrastructure.layout:
            # If discard_empty_racks is True, skip parts without equipment selected for
            # representation.
            if (
                self.parameters.infrastructure.discard_empty_racks
                and not self._part_contains_selected_equipment(part)
            ):
                continue
            # If other_racks is True, select all racks in part rack row.
            if self.parameters.infrastructure.other_racks:
                for rack in part.rack.row.racks:
                    add_rack(rack)
            # Else select all racks in part.
            else:
                add_rack(part.rack)
            if part.rack.row not in rows:
                rows.append(part.rack.row)

        if not racks:
            raise RacksDBDrawingError(
                "Unable to find racks to draw with filters provided in drawing "
                "parameters"
            )
        return racks, rows

    def _rack_preceding_widths(self, rack):
        """Yield the widths (in mm) of all racks and empty slots in rack row
        before the given rack."""
        filled_slots = {}
        for row_rack in rack.row.racks:
            if row_rack.slot < rack.slot:
                yield row_rack.type.width
                filled_slots[row_rack.slot] = row_rack
        # filling empty slots with previous rack width
        for slot in range(rack.slot):
            if slot not in filled_slots:
                logger.debug("Row %s slot %d is not filled", rack.row.name, slot)
                last_rack_width = 0
                reversed_slot = slot
                for reversed_slot in range(slot, 0, -1):
                    if reversed_slot in filled_slots:
                        last_rack_width = filled_slots[reversed_slot].type.width
                        break
                if not (last_rack_width):
                    last_rack_width = self.db.types.racks.first().width
                yield last_rack_width

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
