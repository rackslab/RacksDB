# Copyright (c) 2023 Rackslab
#
# This file is part of RacksDB.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from pathlib import Path
import io
import logging

from flask import Flask, Blueprint, Response, request, send_file

from .. import RacksDB
from ..version import get_version
from ..views import RacksDBViews
from ..generic.openapi import OpenAPIGenerator
from ..generic.dumpers import DBDumperFactory, SchemaDumperFactory
from ..drawers import InfrastructureDrawer, RoomDrawer

logger = logging.getLogger(__name__)


class RacksDBRESTAPIBlueprint(Blueprint):
    MIMETYPES = {
        "json": "application/json",
        "yaml": "application/x-yaml",
        "png": "image/png",
        "svg": "image/svg+xml",
        "pdf": "application/pdf",
    }

    def __init__(
        self,
        schema=RacksDB.DEFAULT_SCHEMA,
        ext=RacksDB.DEFAULT_EXT,
        db=RacksDB.DEFAULT_DB,
        openapi=False,
    ):
        super().__init__("RacksDB REST API blueprint", __name__)
        self.db = RacksDB.load(schema=schema, ext=ext, db=db)
        self.views = RacksDBViews()
        self.add_url_rule("/schema", view_func=self._schema, methods=["GET"])
        self.add_url_rule("/dump", view_func=self._dump, methods=["GET"])
        if openapi:
            self.add_url_rule("/openapi.yaml", view_func=self._openapi, methods=["GET"])
        self.add_url_rule("/<content>", view_func=self._dump_view, methods=["GET"])

        for action in self.views.actions():
            # add path with generic action
            self.add_url_rule(
                action.path,
                view_func=getattr(self, f"_{action.name}"),
                methods=["GET"],
            )

    def _schema(self):
        return Response(
            response=SchemaDumperFactory.get("yaml")().dump(self.db._schema),
            mimetype=self.MIMETYPES["yaml"],
        )

    def _dump(self):
        return Response(
            response=DBDumperFactory.get("yaml")().dump(self.db._loader.content),
            mimetype=self.MIMETYPES["yaml"],
        )

    def _dump_view(self, content):
        data = getattr(self.db, content)
        view = self.views[content]
        filters = {}
        for _filter in view.filters:
            value = request.args.get(_filter.name)
            if value is not None and _filter.nargs is not None:
                value = value.split(",")
            filters[_filter.name] = value
        data = data.filter(**filters)

        if "list" in request.args:
            data = [item.name for item in data]

        dump_format = request.args.get("format", "json")
        dumper = DBDumperFactory.get(dump_format)(
            show_types="with_objects_types" in request.args,
            objects_map=view.objects_map,
            fold="fold" in request.args,
        )
        return Response(
            response=dumper.dump(data), mimetype=self.MIMETYPES[dump_format]
        )

    def _draw(self, entity, name, format):
        file = io.BytesIO()
        if entity == "infrastructure":
            drawer = InfrastructureDrawer(self.db, name, file, format)
        elif entity == "room":
            drawer = RoomDrawer(self.db, name, file, format)
        drawer.draw()
        file.seek(0)
        return send_file(
            file,
            mimetype=self.MIMETYPES[format],
        )

    def _openapi(self):
        dumper = DBDumperFactory.get("yaml")()
        data = OpenAPIGenerator(self.db, self.views).generate()
        return Response(response=dumper.dump(data), mimetype=self.MIMETYPES["yaml"])


class RacksDBRESTAPIApp(Flask):
    def __init__(self):
        super().__init__("RacksDB REST API server")
        parser = argparse.ArgumentParser(description="Do something with RacksDB.")
        parser.add_argument(
            "-v",
            "--version",
            dest="version",
            action="version",
            version="RacksDB " + get_version(),
        )
        parser.add_argument(
            "--debug",
            dest="debug",
            action="store_true",
            help="Enable debug mode",
        )
        parser.add_argument(
            "-s",
            "--schema",
            help="Schema to load (default: %(default)s)",
            default=RacksDB.DEFAULT_SCHEMA,
            type=Path,
        )
        parser.add_argument(
            "-e",
            "--ext",
            help="Path to extensions of schema (default: %(default)s)",
            default=RacksDB.DEFAULT_EXT,
            type=Path,
        )
        parser.add_argument(
            "-b",
            "--db",
            help="Database to load (default: %(default)s)",
            default=RacksDB.DEFAULT_DB,
            type=Path,
        )
        parser.add_argument(
            "--host",
            help="Binding interface for listening socket (default: %(default)s)",
            default="localhost",
        )
        parser.add_argument(
            "-p",
            "--port",
            help="TCP port for listening socket (default: %(default)s)",
            default=5000,
            type=int,
        )
        parser.add_argument(
            "--cors",
            action="store_true",
            help="Enable CORS headers",
        )
        parser.add_argument(
            "--openapi",
            action="store_true",
            help="Enable OpenAPI route",
        )

        self.args = parser.parse_args()
        self.register_blueprint(
            RacksDBRESTAPIBlueprint(
                self.args.schema, self.args.ext, self.args.db, self.args.openapi
            )
        )

    def serve(self):
        logger.info("Running RacksDB REST API application")
        if self.args.cors:
            from flask_cors import CORS

            CORS(self)
        super().run(
            host=self.args.host,
            port=self.args.port,
            debug=self.args.debug,
        )

    @classmethod
    def run(cls):
        app = cls()
        app.serve()
