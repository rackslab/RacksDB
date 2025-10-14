# Copyright (c) 2025 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: MIT

import json

import flask


class RacksDBCustomTestResponse(flask.Response):
    """Custom flask Response class to backport text property of
    werkzeug.test.TestResponse class on werkzeug < 0.15."""

    @property
    def text(self):
        return self.get_data(as_text=True)

    @property
    def json(self):
        if self.mimetype != "application/json":
            return None
        return json.loads(self.text)
