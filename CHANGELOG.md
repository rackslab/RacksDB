# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- schema:
  - Add support of optional list of GPU on _NodeType_ (from @btravouillon).
  - Add optional _initial_ property on _RackType_ to define initial slot index.
- core:
  - Add `bits` defined type.
  - Add `watts` defined type (#23).
- docs:
  - Mention web extra package installation from PyPI in quickstart guide.
  - Mention new optional list of _NodeTypeGpu_ on _NodeType_ in OpenAPI
    specification and structure reference documentation (from @btravouillon).
  - Add nodetype with GPU in examples databases.
  - Mention new `~bits` and `~watts` defined types.

### Changed
- schema: Use `~bits` defined type instead of `~bytes` for _NodeTypeNetif_,
  _StorageEquipmentTypeNetif_ and _NetworkEquipmentTypeNetif_ bandwidth
  properties (#21).
- draw: Start rack slot numbering from rack type initial index (1 by default)
  instead of hard-coded 0 in infrastructure graphical representations (#24).
- docs:
  - Update supported Linux distributions in quickstart guide.
  - Update structure reference documentation and OpenAPI specification after
    bandwidths defined type changed from `~bytes` to `~bits`.
  - Use `~watts` defined type in example extension and extension documentation.

### Fixed
- schema: Fix typo on example attributes on some properties eventually.
- draw: Fix inverted represention of reversed racks row in infrastructures (#27)
  (from @btravouillon)
- docs:
  - Fix URLs to defined types in structure reference after module rename (from
    @btravouillon).
  - Add missing properties examples in OpenAPI specification.

### Removed
- core: Remove support of bits (`[MBG]b`) suffix on `bytes` defined type in
  favor of new `bits` defined type.

## [0.2.0] - 2023-10-25

### Added
- core:
  - Add dumper for JSON format (#3).
  - Add possibility to keep expandable objects folded in dumpers.
  - Support loading sequence of objects with key property as a mapping whose
    keys are the key property of the contained objects.
  - Add examples for some properties in schema.
  - Add native class property on all SchemaDefinedTypes to declare the native
    type returned by the defined type after parsing.
  - Report defined type native type in schema dumps.
- cli:
  - Add format option for datacenters, nodes, racks and infrastructures
    subcommands to control output format.
  - Add fold option to control folding of expandable objects in outputs of
    datacenters, nodes, racks and infrastructures subcommands.
  - Add possibility to select output format of the list of datacenters,
    infrastructures, nodes and racks names.
- web: New executable `racksdb-web` to serve HTTP REST API.
- lib:
  - Add RacksDB.racks property to get the full list of racks.
  - Add possibility to filter list Racks by name.
  - Add RacksDBRack.fillrate computed property.
  - Add support for len(DBList).
  - Add RacksDBRacksRow.nbracks computed property.
- docs:
  - Add installation method from sources intended to software developers in the
    quickstart guide.
  - Add the _« Release notes »_ page based on the content of `CHANGELOG.md`.
  - Mention `--format` and `--fold` options in manpage.
  - Update splitted database examples to demonstrate the possibility to declare
    sequence of objects with key property as mappings.
  - Mention sequence/mapping equivalence for list of objects with keys in
    concepts page.
  - Mention new `racks` attribute on `RacksDB` class specialization in library
    API reference.
  - Mention `nodes`, `fillrate` computed property and filtering capability on
    `RacksDBRack` class specialization in library API reference.
  - Mention `nbracks` computed property on `RacksDBRacksRow` class
    specialization in library API reference.
  - Mention available examples in database files page.
  - Add REST API reference documentation based on OpenAPI specification.
  - Add manpage for `racksdb-web(1)`.
  - Add _Data Visibility_ section to illustrate custom data in extension page.

### Changed
- schema:
  - Rename objects:
    - `DatacenterRoomRack` → `Rack`
    - `DatacenterRoomRow` → `RacksRow`
    - `DatacenterRoomPosition` → `RacksRowPosition`
- core:
  - Introduce DBDict objects that inherit from standard Python dict to handle
    list of objects with keys (#15).
  - New schema format with properties specifications as mapping/hash
  - Schema dumps are now the raw data loaded in schema YAML files and defined
    types instead of an interpreted output.
- lib:
  - RacksDB.nodes and RacksDBInfrastructure.nodes attributes are now DBDict
    of unexpanded nodes.
  - Store datacenters, infrastructures and nodes tags in DBList objects.
- docs:
  - Present the supported Linux distributions with tabs in the quickstart
    guide.
  - Mention key attribute on {Network,Storage}Equipment.name property in
    structure reference.
  - Move database concepts in a dedicated page.
  - Update library API reference and examples with new `DBDict` class and
    changes on `DBList` class.
  - Load of extension example due to missing rack type.
  - Update quickstart guide to mention Python library and REST API.
  - Update schema and extensions pages to document new schema file format.

### Fixed
- core: Rename module that contains defined types definitions dtypes to avoid
  potential conflict with Python standard library types module (#18).
- cli: Catch RacksDB internal errors to report in command output and exit with
  return code 1.
- schema: Add key attribute on {Network,Storage}Equipment.name property.
- docs: Fix spelling in schema extension page.

### Removed
- core: Drop support optional [] attribute suffix for expandable properties.
- docs: Mention of `tags` attributes in library API reference on
  `RacksDBDatacenter`, `RacksDBDatacenter` and `RacksDBNode` classes
  specializations.

## [0.1.0~beta] - 2022-11-28

[unreleased]: https://github.com/rackslab/racksdb/compare/v0.2.0...HEAD
[0.1.0~beta]: https://github.com/rackslab/racksdb/releases/tag/v0.1.0-beta
[0.2.0]: https://github.com/rackslab/racksdb/releases/tag/v0.2.0
