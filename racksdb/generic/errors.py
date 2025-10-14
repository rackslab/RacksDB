# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT


class DBSchemaError(Exception):
    pass


class DBFormatError(Exception):
    pass


class DBDumperError(Exception):
    pass


class DBViewError(Exception):
    pass


class DBOpenAPIGeneratorError(Exception):
    pass
