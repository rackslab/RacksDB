# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Added
- docs: Mention support of Fedora 42.

### Changed
- docs: Reword s/modelize/modeling/.

### Removed
- docs: Drop support of Fedora 40.

## [0.5.0] - 2025-03-26

### Added
- lib:
  - Add `racks` and `racks_tags` properties on `RacksDBDatacenter`
    specialization class.
  - Add `nodes_tags` property on `RacksDBInfrastructure` specialization class.
  - Introduce `RacksDBRequestError` and `RacksDBNotFoundError` errors as
    children of generic `RacksDBError`.
  - Add `tags()` method to `RacksDB` class to search for tags associated to
    either infrastructures, nodes, datacenters or racks.
- draw:
  - Add rack `labels` boolean drawing parameter to control presence of rack
    labels in infrastructure graphical representations, true by default (#89).
  - Add row `labels` boolean drawing parameter to control presence of row
    labels in infrastructure graphical representations, true by default (#90).
  - Add many drawings parameters to tune infrastructure axonometric graphical
    representations.
  - Support axonometric graphical representation of infrastructures (#91→#123).
- cli: Add `tags` command to retrieve tags associated to objects (#102).
- web:
  - Add `tags` endpoint to retrieve tags associated to objects.
  - Support GET method on `draw` endpoint with drawing parameters as optional
    request arguments (#66→#122).
- docs:
  - Mention `tags` command in `racksdb` manpage.
  - Mention `RacksDB.tags()` method in library reference documentation.
  - Mention `RacksDBDatacenter.{racks,racks_tags}` attributes in library
    reference documentation.
  - Mention `RacksDBInfrastructure.nodes_tags` attribute in library reference
    documentation.
  - Add _Integrations_ page with ClusterShell integration howto (#92).
  - Mention axonometric graphical representations in diagrams section of
    overview page and README.
- pkgs:
  - Add dependency on `RFL.log` external library.
  - Add test dependency on `parameterized` external library.

### Changed
- cli: Adopt colored logger from `RFL.log` library (#103).
- web: Update description of HTTP/400 error on `draw` REST API endpoint in
  OpenAPI description to mention all new cases.
- draw: change rack pane default color from #000000 (black) to #262626 (dark
  grey).
- docs:
  - Mention support on Ubuntu 24.04 LTS, Fedora 40 and 41.
  - Format files and directories paths with specific style in quickstart guide.
  - Update OpenAPI description for REST API documentation.
  - Update drawing parameters reference doc.
  - Add some data in example database.
- pkg: Add _tests_ extra packages with all dependencies required to run unit
  tests.

### Fixed
- Support database files with both `.yml` and `.yaml` extensions (#101).
- lib: Support infrastructure without tags in infrastructures `filter()` method.
- core:
  - String representation of computed property.
  - Add current schema object in set of loaded classes to fix resolution of
    references in some corner cases.
- draw:
  - Detect when unable to find racks to draw in infrastructure and raise
    specific exception instead of crashing with `ZeroDivisionError` (#97→#100).
  - Raise `RacksDBDrawingError` when drawer is called with an unsupported
    output image format.
  - Remove unnecessary rack offset at the top of infrastructure graphical
    representation.
- docs:
  - Wrong APT sources file extension in quickstart guide.
  - Path of system packages examples directory in quickstart guide.
- web:
  - Fix format of array items type description format in OpenAPI description
    generator.
  - Fix Path type of RacksDBWebBlueprint arguments default values.
  - Setup colored logger from `RFL.log` library and honor `--debug` command line
    option of `racksdb-web`.
  - Log critical error instead of crashing when `racksdb-web` is unable to load
    schema or database (#110).
  - Return HTTP/400 error when draw endpoint is called with unsupported image
    format.
  - Return HTTP/400 error when draw endpoint is called with unsupported entity.
- ui:
  - Limit specs links size in equipment type modal (#76).
  - Update bundled dependencies to fix security issues CVE-2024-39338,
    CVE-2025-27152 (axios),
    CVE-2024-4068 (braces), CVE-2024-31207, CVE-2024-45812, CVE-2024-45811,
    CVE-2025-24010, CVE-2025-30208 (vite), CVE-2024-6783
    (vue-template-compiler), CVE-2024-37890 (ws), CVE-2024-21538 (cross-spawn),
    CVE-2024-4067 (micromatch), CVE-2024-47068 (rollup), CVE-2024-55565
    (nanoid), CVE-2025-24964 (vitest) and GHSA-67mh-4wv8-2f99 (esbuild).
- pkg: Fix `pkg_resources` API deprecation error by using importlib module and
  `importlib_metadata` external backport library for Python < 3.8 (#104).

### Removed
- docs: Remove mention of support on Fedora 39 and 38.

## [0.4.0] - 2024-04-15

### Added
- lib:
  - Add advanced `tags` property and `_filter()` method specializations on
    `RacksDBStorageEquipment`, `RacksDBNetworkEquipment` and
    `RacksDBSMiscEquipment` classes, similarly to `RacksDBNode`.
  - Introduce `RacksDBSchemaError` and `RacksDBFormatError` in order to easily
    catch these errors from other software that use RacksDB as an external
    library.
  - Add optional `path` property to `DBLoader` class.
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
  - Add `--with-ui` option to enabled web UI in `racksdb-web`.
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
- schema:
  - Add `position` computed property on `Node`, `StorageEquipment`,
    `NetworkEquipment` and `MiscEquipment` objects to get their exact position
    in the racks (#72).
  - Introduce `DatacenterLocation` object attached to `Datacenter` optional
    location property to define GPS coordinates of the datacenters.
- ui:
  - Add map of datacenters if datacenters view with their geographical
    positions if defined in database (#43).
  - Add possibility to filter equipment in infrastructure by rack, equipment
    category, equipment type, equipment name and tags (#42).
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
  - Mention new `--with-ui` option in `racksdb-web` manpage.

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
- web:
  - Change some HTTP status code to report errors on `draw` action endpoint:
    - 415 → 500 when unable to load drawing parameters schema.
    - 415 → 400 when unable to load drawing parameters.
    - 415 → 400 for unsupported coordinates format.
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
- pkg: Move Flask-Cors python dependency in _dev_ variant package.
- docs:
  - Update supported Linux distributions in quickstart guide (add fedora 39 and
    RHEL9, drop fedora 37 and Ubuntu 22.04 LTS).
  - Update OpenAPI description for REST API documentation.
  - Update drawing parameters reference doc.

### Fixed
- ui: Bump missed version number in UI application metadata.
- core:
  - Fix dump of properties in JSON and YAML when not defined in database but
    overriden by specialized classes.
  - Fix folded equipment name filtering (#73).
  - Add missing raise instructions in some DB format error cases.
  - Avoid reporting duplicated tags when defined on both parent part and
    equipment (#77).
- web:
  - Send HTTP/400 status code when JSON error instead of crashing with
    exception in case of error when drawing an infrastructure or a room.
  - Warn instead of crash when CORS is enabled but the corresponding
    Flask-Cors module cannot be imported.
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
  - Add web UI user guide page (#44).
  - Commands to install web UI from source in quickstart guide.
  - Documentation to server web UI with `racksdb-web` in quickstart guide.
  - Mention web UI feature in home page and features overview.

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

[unreleased]: https://github.com/rackslab/racksdb/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/rackslab/racksdb/releases/tag/v0.5.0
[0.4.0]: https://github.com/rackslab/racksdb/releases/tag/v0.4.0
[0.3.0]: https://github.com/rackslab/racksdb/releases/tag/v0.3.0
[0.2.0]: https://github.com/rackslab/racksdb/releases/tag/v0.2.0
[0.1.0~beta]: https://github.com/rackslab/racksdb/releases/tag/v0.1.0-beta
