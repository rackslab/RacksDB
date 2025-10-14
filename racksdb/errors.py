# Copyright (c) 2022-2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT


from .generic.errors import DBFormatError, DBSchemaError


class RacksDBError(Exception):
    pass


class RacksDBRequestError(RacksDBError):
    pass


class RacksDBNotFoundError(RacksDBError):
    pass


class RacksDBFormatError(DBFormatError):
    pass


class RacksDBSchemaError(DBSchemaError):
    pass


class RacksDBDrawingError(RacksDBError):
    pass
