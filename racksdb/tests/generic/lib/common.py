# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later


from racksdb.generic.schema import Schema
from racksdb.generic.definedtype import SchemaDefinedType
from racksdb.generic.db import DBDictsLoader, GenericDB

from . import bases

VALID_SCHEMA = {
    "_version": "1",
    "_content": {
        "properties": {
            "apples": {"type": "list[:Apple]"},
            "pear": {"type": ":Pear"},
            "bananas": {"type": "list[:BananaOrigin]", "optional": True},
            "stock": {"type": ":AppleStock"},
        }
    },
    "_objects": {
        "Apple": {
            "properties": {
                "name": {
                    "type": "str",
                    "key": True,
                },
                "color": {
                    "type": "str",
                },
                "weight": {"type": "~weight"},
            }
        },
        "Pear": {
            "properties": {
                "color": {"type": "str", "default": "yellow"},
                "weight": {
                    "type": "~weight",
                },
                "variety": {
                    "type": "str",
                },
            }
        },
        "BananaOrigin": {
            "description": "Bananas producers",
            "properties": {
                "origin": {
                    "type": "str",
                },
                "market_share": {
                    "type": "float",
                },
                "species": {"type": "list[:Banana]"},
            },
        },
        "Banana": {
            "properties": {
                "name": {
                    "type": "str",
                    "key": True,
                },
                "color": {
                    "type": "str",
                },
                "origin": {
                    "type": "^BananaOrigin",
                },
                "edible": {"type": "bool", "default": True},
            }
        },
        "AppleStock": {
            "properties": {
                "content": {
                    "type": "list[:AppleCrate]",
                },
                "total": {"type": "int", "computed": True},
            },
        },
        "AppleCrate": {
            "properties": {
                "name": {
                    "type": "expandable",
                },
                "id": {
                    "type": "rangeid",
                },
                "species": {
                    "type": "$Apple.name",
                },
                "quantity": {
                    "type": "int",
                },
            }
        },
    },
}

VALID_EXTENSIONS = {
    "_content": {"properties": {"plums": {"type": "list[:Plum]", "default": []}}},
    "_objects": {
        "Pear": {"properties": {"juiciness": {"type": "float", "optional": True}}},
        "Plum": {"properties": {"species": {"type": "str"}}},
    },
}

VALID_DB = {
    "apples": [
        {"name": "golden", "color": "yellow", "weight": "55g"},
        {"name": "granny smith", "color": "green", "weight": "63g"},
    ],
    "pear": {
        "color": "green",
        "weight": "60g",
        "variety": "williams",
    },
    "bananas": [
        {
            "origin": "ecuador",
            "market_share": 0.3,
            "species": {"cavendish": {"color": "yellow"}},
        },
        {
            "origin": "ghana",
            "market_share": 0.2,
            "species": {"plantain": {"color": "green"}},
        },
    ],
    "stock": {
        "content": [
            {
                "name": "crate[01-10]",
                "id": 101,
                "species": "golden",
                "quantity": 30,
            },
            {
                "name": "crate[11-20]",
                "id": 111,
                "species": "granny smith",
                "quantity": 10,
            },
        ],
    },
}


class SchemaDefinedTypeWeight(SchemaDefinedType):

    pattern = r"(\d+)g"
    native = int

    def parse(self, value):
        match = self._match(value)
        size = float(match.group(1))
        return int(size)


VALID_DEFINED_TYPES = {"weight": SchemaDefinedTypeWeight()}


class FakeSchemaLoader:
    def __init__(self, content):
        self.content = content


class FakeTypesLoader:
    def __init__(self, content):
        self.content = content


def valid_schema():
    return Schema(FakeSchemaLoader(VALID_SCHEMA), FakeTypesLoader(VALID_DEFINED_TYPES))


def valid_loader():
    return DBDictsLoader(VALID_DB)


def valid_db():
    db = GenericDB("Test", valid_schema(), bases)
    db.load(valid_loader())
    return db
