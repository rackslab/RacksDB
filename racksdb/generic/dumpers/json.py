# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any
import json
import logging

from ...generic.db import DBObject, DBObjectRange, DBObjectRangeId, DBDict

logger = logging.getLogger(__name__)


class GenericJSONEncoder(json.JSONEncoder):
    def __init__(self, objects_map={}, **kwargs):
        super().__init__(**kwargs)
        self.objects_map = objects_map

    def default(self, obj: Any) -> Any:
        if isinstance(obj, DBObjectRange):
            return str(obj.rangeset)
        elif isinstance(obj, DBObjectRangeId):
            return obj.start
        elif isinstance(obj, DBDict):
            return [self.default(item) for item in obj.values()]
        elif isinstance(obj, DBObject):
            result = {}
            for attribute, value in vars(obj).items():
                # Skip special attributes
                if attribute in [
                    "_db",
                    "_indexes",
                    "_schema",
                    "_parent",
                    "_first",
                    "_key",
                ]:
                    continue
                # Replace renamed attribute by overriding property
                if attribute.startswith(obj.LOADED_PREFIX):
                    attribute = attribute[len(obj.LOADED_PREFIX) :]
                    value = getattr(obj, attribute)
                # Check the object is mapped to one of its attribute or None.
                if value.__class__.__name__ in self.objects_map.keys():
                    # If the object is mapped to None, discard the attribute and
                    # continue to the next one.
                    if self.objects_map[value.__class__.__name__] is None:
                        continue
                    # Else, map the object to one of its attribute.
                    value = getattr(value, self.objects_map[value.__class__.__name__])
                if isinstance(value, DBObject) or isinstance(value, DBDict):
                    result[attribute] = self.default(value)
                else:
                    result[attribute] = value
            return result
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


class DBDumperJSON:
    def __init__(self, show_types=False, objects_map={}):
        self.objects_map = objects_map

    def dump(self, obj: Any) -> str:
        # DBDict are also standard python dictionnaries, then json.JSONEncoder thinks it
        # can handle without hurdle and it does not call GenericJSONEncoder.default()
        # for this obj type. However:
        #
        # - DBDict must be represented as a list of values in dumps, the keys must not
        #   be represented as they are just defined for pratical reasons to facilitate
        #   data manipulation in library.
        # - Keys can be DBObjectRange objects that cannot be represented by standard
        #   json.JSONEncoder.
        #
        # For these reasons, DBDict is converted here as a standard list of values.
        if isinstance(obj, DBDict):
            obj = [item for item in obj.values()]
        return GenericJSONEncoder(objects_map=self.objects_map).encode(obj)
