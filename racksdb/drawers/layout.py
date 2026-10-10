# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

"""Shared layout helpers for room plans and infrastructure diagrams."""

import logging
from itertools import chain

logger = logging.getLogger(__name__)


def rack_slot_offset_x(db, rack, ratio=1.0):
    """Return horizontal offset of rack top-left in row coordinates, in the same units
    as rack type widths multiplied by ratio (pixels when ratio is the draw ratio, mm
    when ratio is 1). Matches RoomDrawer slot summing, including empty slots."""
    offset = 0
    filled_slots = {}
    for row_rack in rack.row.racks:
        if row_rack.slot < rack.slot:
            offset += int(row_rack.type.width * ratio)
            filled_slots[row_rack.slot] = row_rack
    for slot in range(rack.slot):
        if slot not in filled_slots:
            logger.debug("Row %s slot %d is not filled", rack.row.name, slot)
            last_rack_width = 0
            for reversed_slot in range(slot, 0, -1):
                if reversed_slot in filled_slots:
                    last_rack_width = filled_slots[reversed_slot].type.width
                    break
            if not last_rack_width:
                last_rack_width = db.types.racks.first().width
            offset += int(last_rack_width * ratio)
    return offset


def part_contains_selected_equipment(part, parameters):
    """Return True if the part contains equipment selected for drawing."""
    if not hasattr(parameters.infrastructure, "equipment_tags"):
        return True
    for equipment in chain(part.nodes, part.storage, part.network, part.misc):
        if any(
            equipment_tag in parameters.infrastructure.equipment_tags
            for equipment_tag in equipment.tags
        ):
            return True
    return False


def equipment_matches_tags(equipment, parameters):
    """Return True if equipment passes equipment_tags filter (or filter is unset)."""
    if not hasattr(parameters.infrastructure, "equipment_tags"):
        return True
    return any(
        equipment_tag in parameters.infrastructure.equipment_tags
        for equipment_tag in equipment.tags
    )


def select_infrastructure_racks(infrastructure, parameters):
    """Return (racks, rack_rows) to represent for an infrastructure diagram."""
    racks = []
    rack_rows = []
    for part in infrastructure.layout:
        if (
            parameters.infrastructure.discard_empty_racks
            and not part_contains_selected_equipment(part, parameters)
        ):
            continue
        if parameters.infrastructure.other_racks:
            for rack in part.rack.row.racks:
                if rack not in racks:
                    racks.append(rack)
        elif part.rack not in racks:
            racks.append(part.rack)
        if part.rack.row not in rack_rows:
            rack_rows.append(part.rack.row)
    return racks, rack_rows


def rack_in_infrastructure(infrastructure, rack):
    for part in infrastructure.layout:
        if part.rack.name == rack.name:
            return True
    return False


def infrastructure_part_for_rack(infrastructure, rack):
    for part in infrastructure.layout:
        if part.rack.name == rack.name:
            return part
    return None
