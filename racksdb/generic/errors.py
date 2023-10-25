# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later


class DBSchemaError(Exception):
    pass


class DBFormatError(Exception):
    pass


class DBDumperError(Exception):
    pass


class DBViewError(Exception):
    pass
