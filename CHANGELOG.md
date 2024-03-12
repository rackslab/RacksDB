# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- lib:
  - Add advanced `tags` property and `_filter()` method specializations on
    `RacksDBStorageEquipment`, `RacksDBNetworkEquipment` and
    `RacksDBSMiscEquipment` classes, similarly to `RacksDBNode`.
  - Export `DBSchemaError` and `DBFormatError` in main module in order to
    facilitate their import from other software that use RacksDB as an external
    library.
- cli: Add `-c, --coordinates` and `--coordinates-format` arguments on
  `racksdb draw` sub-command to generate coordinate file in either JSON or YAML
  format with coordinates of racks and equipment in the image along with the
  image file.
- web:
  - Add `coordinates` and `coordinates_format` query parameter on `draw` action
    enpoint to get coordinates of racks and equipment along with image file in
    multipart response (#56).
  - Optional default drawing parameters in arguments of `RacksDBWebBlueprint`
    used for all requests to `draw` endpoint unless overriden in request body.
- draw:
  - Add general `pixel_perfect` boolean drawing parameter, disabled by default.
    When enabled, RacksDB properly align graphical representation with pixels
    matrix with concession on relative dimensions correctness (#4).
  - Add room `racks_labels` boolean drawing parameter, enabled by default. When
    enabled, RacksDB label all racks with their names in room diagrams (#58).
  - Add infrastructure `equipment_labels` boolean drawing parameter, enabled by
    default. When enabled, RacksDB label equipment with their names in
    infrastructure diagrams (#55).
  - Add infrastructure `equipment_tags` optional drawing parameter to give the
    possibility to select equipment represented in infrastructure diagrams with
    their tags (#57).
  - Add infrastructure `ghost_unselected` boolean drawing parameter, disabled by
    default, to control if unselected equipment is represented as ghosted in
    racks to mark their presence in the infrastructure. When disabled, the
    unselected equipment is simply discarded.
  - Add colors equipment `ghost` drawing parameter to specify the color of
    ghosted equipment.
  - Add infrastructure `discard_empty_racks` boolean drawing parameter, enabled
    by default, to control if racks used by infrastructure that contain only
    unselected equipment are represented in infrastructure diagrams.
  - Add infrastructure `other_racks` boolean drawing parameter to control if
    other racks located in the same rows as the infrastructure are represented,
    even if they do not contain infrastructure equipment. Other racks are
    represented when set to true. It is false by default (#61).
  - Add support for optional alpha channel in `~hexcolor` defined type (#65).
  - Make racks labels scalable to avoid exceeding rack width in infrastructure
    diagrams (#69).
- schema: Add `position` computed property on `Node`, `StorageEquipment`,
  `NetworkEquipment` and `MiscEquipment` objects to get their exact position in
  the racks (#72).
- pkg:
  - Add dependency on PyGObject python library (used to call Pango library).
  - Add optional dependency on requests-toolbelt python library on web variant
    to generate multipart response with graphical representations images and
    coordinates.
- docs:
  - Mention development libraries required for external dependencies in
    Quickstart guide.
  - Mention new class specializations on `RacksDBStorageEquipment`,
    `RacksDBNetworkEquipment` and `RacksDBSMiscEquipment` in library reference
    documentation.
  - Update `racksdb` manpage to mention `-c, --coordinates` and
    `--coordinates-format` arguments on `racksdb draw` sub-command.
  - Mention optional alpha channel in documentation of drawing parameters
    `~hexcolor` defined type.
  - Mention concept of computed property with the corresponding attribute.

### Changed
- draw:
  - Replace Room/Infrastructure `scale` drawing parameters by maximum
    width/height dimensions. RacksDB compute a dynamic ratio based on these
    maximum dimensions to define the sizes of represented racks and equipment in
    pixels.
  - Make font size of text labels on racks and equipment responsive to the size
    of the corresponding items. The font size is reduced, down to its minimum
    size, until the text label fits into the item.
  - Change unit (pixels→mm) and default value (10→40) of Rack `pane_width`
    drawing parameter.
  - In infrastructure diagrams, computed rows widths and heights, thus drawing
    scale eventually, are now based on represented racks by taking into account
    empty racks, `discard_empty_racks` and `other_racks` drawing parameters.
- ui:
  - Many improvements in datacenter details page (#39), such as:
    - The table of rooms is moved upper in the page.
    - The datacenter search input is replaced by a filter input in the top right
      corner to filter rooms by name.
    - The table of rooms does not use all page width anymore.
    - The _"Access to the room"_ button is be renamed _"View room"_.
    - The table header for view room button has been removed.
    - Add button to sort rooms by name in alphabetical order, either in
      ascending or descending order.
    - Adopt the same font as in datacenter room details view.
  - More ergonomic combobox to select datacenter and infrastructure (#38).
  - Many improvements in datacenter room page (#40), such as:
    - The datacenter search input is replaced by a filter input in the top right
      corner to filter racks by name.
    - Improve readability of racks table by reducing its width, add lines
      between rows and increase row height.
    - Add _"Hide empty"_ button to hide empty racks.
    - Add button to invert racks sorting by name in alphabetical order, either
      in ascending or descending order.
    - More accessible dialog to view room map in bigger size which can be closed
      with escape key or by clicking outside.
    - Add link to infrastructure details view in infrastructures list.
    - Add alternative text for the images.
  - Many improvements in infrastructure details page (#41), such as:
    - The cards are removed in favor of the table view only.
    - Equipment tags are displayed in table.
    - The table is splitted by racks sections with grouped rows, sorted by
      names. Racks sections can be closed and opened at will.
    - A button gives the possibility to invert the order of racks.
    - Equipments in racks sections are ordered by position in the racks from
      top to bottom.
    - Readability of equipment table is improved by reducing its width on
      large screens.
    - When the infrastructure image is maximized, it can be closed with
      escape button or by clicking on the sides.
- schema: Declare all computed properties in schema.
- docs:
  - Update supported Linux distributions in quickstart guide (add fedora 39
    and drop fedora 37).
  - Update OpenAPI description for REST API documentation.
  - Update drawing parameters reference doc.

### Fixed
- ui: Bump missed version number in UI application metadata.
- core:
  - Fix dump of properties in JSON and YAML when not defined in database but
    overriden by specialized classes.
  - Fix folded equipment name filtering (#73).
- docs: Add missing version in example REST API queries.

### Removed
- docs: Remove mention of computed properties in Python library reference
  documentation as computed properties are now properly declared along with back
  references in database structure reference documentation.

## [0.3.0] - 2024-01-22

### Added
- ui: new web UI (in _beta_ version)
- schema:
  - Add support of optional list of GPU on _NodeType_ (from @btravouillon).
  - Add optional _initial_ property on _RackType_ to define initial slot index.
  - Add support of miscellaneous equipments with _MiscEquipmentType_ and
    _MiscEquipment_ objects (#29).
  - Add support of `:recursive` object default to make the property default the
    corresponding object with all its defaults properties recursively.
  - Add optional _tags_ property on _Rack_ objects.
- core:
  - Add `bits` defined type.
  - Add `watts` defined type (#23).
- cli: Add `--parameters` and `--drawings-schema` options to _draw_ subcommands
  to specify paths to respectively drawing parameters database and drawing
  parameters schema in YAML format.
- draw:
  - Add schema for drawing parameters.
  - Add possibility to tune drawings settings (eg. margin, spacing, etc) with
    drawings parameters.
  - Add `~hexcolor` defined type.
  - Add possiblity to define racks and equipment coloring rules with tags and
    type associations in drawing parameters (#34).
- docs:
  - Mention web extra package installation from PyPI in quickstart guide.
  - Mention new optional list of _NodeTypeGpu_ on _NodeType_ in OpenAPI
    specification and structure reference documentation (from @btravouillon).
  - Add nodetype with GPU in examples databases.
  - Mention new `~bits` and `~watts` defined types.
  - Mention new optional _initial_ property on _RackType_ in structure reference
    documentation and OpenAPI specification.
  - Mention new _MiscEquipmentType_ and _MiscEquipment_ objects in OpenAPI
    specification and structure reference documentation.
  - Add miscellaneous equipment in example database.
  - Mention drawing parameters options `--parameters` and `--drawings-schema`
    options in `racksdb` and `racksdb-web` manpages.
  - Add documentation page for drawing parameters with howto and reference.
  - Mention new _tags_ property on _Rack_ object in reference documentation.
  - Mention schema properties default `:recursive` special value in schema
    documentation.
  - Prefix objects from RacksDB shema with `RacksDB` and add objects from
    drawing parameters schema in OpenAPI specification and structure reference
    documentation.
  - Add new datacenter and infrastructures in example database.

### Changed
- Database schema is moved from `/usr/share/racksdb/schema.yml` to
  `/usr/share/racksdb/schemas/racksdb.yml`.
- schema: Use `~bits` defined type instead of `~bytes` for _NodeTypeNetif_,
  _StorageEquipmentTypeNetif_ and _NetworkEquipmentTypeNetif_ bandwidth
  properties (#21).
- draw: Start rack slot numbering from rack type initial index (1 by default)
  instead of hard-coded 0 in infrastructure graphical representations (#24).
- web:
  - Return REST API errors in JSON object.
  - Changed /draw route method from GET to POST with optional JSON or YAML
    drawing parameters in request body.
  - Add version to REST API paths.
- docs:
  - Update supported Linux distributions in quickstart guide.
  - Update structure reference documentation and OpenAPI specification after
    bandwidths defined type changed from `~bytes` to `~bits`.
  - Use `~watts` defined type in example extension and extension documentation.
  - Update examples database to new rack type initial slot index value set to 1.
  - Update equipments positionning howto to mention new default initial slot 1
    and possibility to change it in database.
  - Report default value as example in REST API reference documentation when
    example is not defined in schema.
  - Update REST API reference documentation paths with version.

### Fixed
- core:
  - Warn with message instead of failing with stack trace when defined type
    module cannot be loaded.
  - Report error instead of stack trace when the content of an object is not a
    valid mapping of properties.
- schema: Fix typo on example attributes of some properties.
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
[0.3.0]: https://github.com/rackslab/racksdb/releases/tag/v0.3.0
