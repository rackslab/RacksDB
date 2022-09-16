import unittest

from racksdb.generic.schema import SchemaDefinedTypeLoader
from racksdb.generic.definedtype import SchemaDefinedType


class TestSchemaDefinedTypeLoader(unittest.TestCase):
    def test_schema_defined_type_loader(self):
        # Load defined types provided in RacksDB
        loader = SchemaDefinedTypeLoader('racksdb.types')
        # Verify at least one defined type has been loaded
        self.assertGreater(len(loader.content), 0)
        # Verify loader content is a dict
        self.assertIs(type(loader.content), dict)
        # Verify content values are valid SchemaDefinedType
        for defined_type in loader.content.values():
            self.assertIsInstance(defined_type, SchemaDefinedType)
