# RacksDB

## Description

RacksDB is a YAML based database format to describe the architecture of hardware
infrastructures in datacenters (racks, servers, cables, etc), accompanied by its
reference tool and library.

This is a simple CMDB/DCIM tool that can help system administrators on the
following subjects:

* Architecture : Generate architecture diagrams, IP addressing plan, SPOFs
  detection
* Configuration : Data source for configuration management and templates
* Documentation : Definition of generic and programmable administration
  procedures, better infrastructure perception for users and administrators
* Monitoring : Dashboard production, rules-based configuration generation
* Inventory : Coherency control, acceptance testing

RacksDB can be seen as a simple and partial alternative to
[NetBox](https://netbox.dev/) or [RackTables](https://www.racktables.org/).

This Git repository contains the specifications of RacksDB format and a
reference implementation of tool and library to extract information from the
databases.

## Status

This is a prototype of an ongoing work.

## Authors

RacksDB is developped and maintained by [Rackslab](https://rackslab.io).

## License

RacksDB is distributed under the terms of the GNU General Public License v3.0 or
later (GPLv3+).
