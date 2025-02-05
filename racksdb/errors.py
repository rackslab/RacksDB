# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later


from .generic.errors import DBFormatError, DBSchemaError


class RacksDBError(Exception):
    pass


class RacksDBFormatError(DBFormatError):
    pass


class RacksDBSchemaError(DBSchemaError):
    pass


class RacksDBDrawingError(RacksDBError):
    pass
