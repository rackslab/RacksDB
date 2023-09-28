# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- core:
  - Add dumper for JSON format (#3).
  - Add possibility to keep expandable objects folded in dumpers.
  - Support loading sequence of objects with key property as a mapping whose
    keys are the key property of the contained objects.
- cli:
  - Add format option for datacenters, nodes, racks and infrastructures
    subcommands to control output format.
  - Add fold option to control folding of expandable objects in outputs of
    datacenters, nodes, racks and infrastructures subcommands.
  - Add possibility to select output format of the list of datacenters,
    infrastructures, nodes and racks names.
- lib:
  - Add RacksDB.racks property to get the full list of racks.
  - Add possibility to filter list DatacenterRoomRack by name.
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
  - Mention `nodes` computed property and filtering capability on
    `RacksDBDatacenterRoomRack` class specialization in library API reference.

### Changed
- core: Introduce DBDict objects that inherit from standard Python dict to
  handle list of objects with keys (#15).
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

### Fixed
- core: Rename module that contains defined types definitions dtypes to avoid
  potential conflict with Python standard library types module (#18).
- cli: Catch RacksDB internal errors to report in command output and exit with
  return code 1.
- schema: Add key attribute on {Network,Storage}Equipment.name property.

### Removed
- core: Drop support optional [] attribute suffix for expandable properties.
- docs: Mention of `tags` attributes in library API reference on
  `RacksDBDatacenter`, `RacksDBDatacenter` and `RacksDBNode` classes
  specializations.

## [0.1.0~beta] - 2022-11-28

[unreleased]: https://github.com/rackslab/racksdb/compare/v0.1.0-beta...HEAD
[0.1.0~beta]: https://github.com/rackslab/racksdb/releases/tag/v0.1.0-beta
