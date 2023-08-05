from dashmat.server.react import ReactServer
from dashmat.scheduler import Scheduler

from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop

from flask import send_from_directory, render_template, abort
from werkzeug.routing import PathConverter
from flask import Flask

from functools import wraps
from textwrap import dedent
import pkg_resources
import threading
import tempfile
import logging
import shutil
import flask
import time
import json
import six
import os

log = logging.getLogger("dashmat.server")

here = os.path.dirname(__file__)

class Server(object):
    def __init__(self, host, port, debug, dashboards, modules, module_options, datastore, dynamic_dashboard_js, compiled_static_prep, compiled_static_folder, without_checks):
        self.thread_stopper = {"finished": False}

        self.host = host
        self.port = port
        self.modules = modules
        self.datastore = datastore
        self.dashboards = dashboards
        self.module_options = module_options
        self.without_checks = without_checks
        self.dynamic_dashboard_js = dynamic_dashboard_js

        self.compiled_static_prep = compiled_static_prep
        self.compiled_static_folder = compiled_static_folder

        self.react_server = ReactServer()

    def serve(self):
        http_server = HTTPServer(WSGIContainer(self.app))
        scheduler = Scheduler(self.datastore)
        if not self.without_checks:
            for name, (module, server) in self.servers.items():
                scheduler.register(module, server, name)

        try:
            if not self.without_checks:
                scheduler.start()
            http_server.listen(self.port, self.host)
            log.info("Starting server on http://%s:%s", self.host, self.port)

            try:
                IOLoop.instance().start()
            finally:
                self.thread_stopper["finished"] = True
        finally:
            scheduler.finish()

    @property
    def app(self):
        if getattr(self, "_app", None) is None:
            self._app = Flask("dashmat.server")

            # Remove auto generated static route
            while self._app.url_map._rules:
                self._app.url_map._rules.pop()
            for key in list(self._app.url_map._rules_by_endpoint):
                self._app.url_map._rules_by_endpoint.pop(key)
            self._app.url_map.update()
            self._app.view_functions.clear()

            self.servers = {}
            for name, module in self.modules.items():
                self.servers[name] = (module, module.make_server(self.module_options[name].server_options))

            # Register our own routes
            self.register_routes(self._app)

            if self.dynamic_dashboard_js:
                # Prepare the docker image for translating jsx into javascript
                deps = {}
                for _, module in sorted(self.modules.items()):
                    deps.update(module.npm_deps())
                self.react_server.prepare(deps, self.compiled_static_folder)
        return self._app

    def register_routes(self, app):
        class EverythingConverter(PathConverter):
            regex = '.*?'
        app.url_map.converters['everything'] = EverythingConverter

        def make_view(func, module, module_name):
            @wraps(func)
            def wrapper(*args, **kwargs):
                ds = self.datastore.prefixed("{0}-{1}".format(module.relative_to, module_name))
                res = func(ds, *args, **kwargs)
                return flask.jsonify({"value": res})
            return wrapper

        for name, (module, server) in self.servers.items():
            for route_name, func in server.routes:
                view = make_view(func, module, name)
                view.__name__ = "server_route_{0}_{1}".format(name, route_name)
                route = "/data/{0}/{1}".format(name, route_name)
                log.info("Adding route %s", route)
                app.route(route)(view)

        @app.route("/diagnostic/status/heartbeat", methods=['GET'])
        def heartbeat():
            return ""

        @app.route("/diagnostic/status/nagios", methods=['GET'])
        def nagios():
            return "OK"

        @app.route("/diagnostic/version", methods=['Get'])
        def version():
            static_dir = os.path.join(here, "static")
            return send_from_directory(static_dir, "version")

        @app.route("/static/dashboards/<everything:path>", methods=["GET"])
        def static_dashboards(path):
            if path not in self.dashboards:
                raise abort(404)

            location = generate_dashboard_js(
                  self.dashboards[path]
                , self.react_server
                , self.compiled_static_folder
                , self.compiled_static_prep
                , self.modules

                , dynamic_dashboard_js = self.dynamic_dashboard_js
                )

            return send_from_directory(os.path.dirname(location), os.path.basename(location))

        @app.route("/static/css/<import_path>/<path:name>", methods=["GET"])
        def static_css(import_path, name):
            static_folder = pkg_resources.resource_filename(import_path, 'static')
            static_file = os.path.join(static_folder, name)
            if os.path.exists(static_file):
                return send_from_directory(static_folder, name)
            else:
                raise abort(404)

        def make_dashboard(path, dashboard):
            def dashboard_view():
                title = path.replace("/", ' ').replace('_', ' ').title()
                css = []
                enabled_modules = list(dashboard.enabled_modules)
                for imprt in dashboard.imports:
                    if hasattr(imprt, "module_name"):
                        if isinstance(imprt.module_name, six.string_types):
                            module = self.modules[imprt.module_name]
                        elif isinstance(imprt.module_name, dict):
                            module = imprt.module_name["import_path"]
                        else:
                            module = imprt.module_name
                        enabled_modules.append(module)

                def add_dependencies():
                    added = False
                    for module in enabled_modules:
                        for dependency in module.dependencies():
                            if self.modules[dependency] not in enabled_modules:
                                enabled_modules.append(self.modules[dependency])
                                added = True
                    if added:
                        add_dependencies()
                add_dependencies()

                first_state = {}
                for module in enabled_modules:
                    css.extend(["/static/css/{0}/{1}".format(module.relative_to, c) for c in module.css()])

                for name, (module, server) in self.servers.items():
                    for route_name, func in server.routes:
                        route = "/data/{0}/{1}".format(name, route_name)
                        ds = self.datastore.prefixed("{0}-{1}".format(module.relative_to, name))
                        first_state[route] = func(ds)

                return render_template('index.html', dashboardjs="/static/dashboards/{0}".format(path), title=title, css=css, first_state=json.dumps(first_state))
            dashboard_view.__name__ = "dashboard_{0}".format(path.replace("_", "__").replace("/", "_"))
            return dashboard_view

        for path, dashboard in self.dashboards.items():
            app.route(path, methods=["GET"])(make_dashboard(path, dashboard))

def generate_dashboard_js(dashboard, react_server, compiled_static_folder, compiled_static_prep, modules, dynamic_dashboard_js=True):
    """
    Given a dashboard, make the bundle javascript for it

    We also do some caching so we don't generate the javascript when nothing has changed

    First we generate the dashboard es6 content with dashboard.make_dashboard_module()
    we then write this to disk if not on disk or hasn't changed.

    If the compiled equivalent is not on disk or the raw has a modified time greater than compiled
    We generate compiled.

    If this is not the case, we find all the static/react folders from our modules
    and determine if anything has a modified time greater than the compiled javascript.

    If nothing does, and we have our compiled javascript, we do nothing.

    If we need to do something, we create a temporary folder with a copy of the raw javascript
    and the static/react folders for each module named with the import_path of the module.

    Finally we add a webpack configuration to this temporary folder and tell react_server to run webpack
    there and generate the compiled javascript.

    Easy!
    """
    javascript = dashboard.make_dashboard_module(modules)

    dashboard_folder = os.path.join(compiled_static_folder, "dashboards")
    if not os.path.exists(dashboard_folder):
        os.makedirs(dashboard_folder)

    filename = dashboard.path.replace("_", "__").replace("/", "_")
    final_location = "{0}.js".format(os.path.join(dashboard_folder, filename))

    if not dynamic_dashboard_js:
        return final_location

    js_location = os.path.join(dashboard_folder, "{0}.js".format(filename))
    raw_location = os.path.join(dashboard_folder, "{0}.raw".format(filename))

    if os.path.exists(raw_location):
        with open(raw_location) as fle:
            if fle.read() != javascript:
                with open(raw_location, 'w') as write_fle:
                    write_fle.write(javascript)
    else:
        with open(raw_location, 'w') as write_fle:
            write_fle.write(javascript)

    do_change = False
    js_mtime = -1 if not os.path.exists(js_location) else os.stat(js_location).st_mtime
    if not os.path.exists(js_location) or os.stat(raw_location).st_mtime > js_mtime:
        do_change = True

    folders = [("dashmat.server", os.path.join(here, "static", "react"))]
    for name, module in modules.items():
        react_folder = pkg_resources.resource_filename(module.relative_to, "static/react")
        if (module.relative_to, react_folder) not in folders:
            if os.path.exists(react_folder):
                if not do_change:
                    for root, dirs, files in os.walk(react_folder, followlinks=True):
                        for fle in files:
                            location = os.path.join(root, fle)
                            if os.stat(location).st_mtime > js_mtime:
                                do_change = True
                                break
                folders.append((module.relative_to, react_folder))

    if do_change:
        directory = None
        try:
            directory = tempfile.mkdtemp(dir=compiled_static_prep)
            shutil.copy(raw_location, os.path.join(directory, "{0}.js".format(filename)))
            for module_path, react_folder in folders:
                dest = os.path.join(directory, module_path)
                shutil.copytree(react_folder, dest)

            with open(os.path.join(directory, "webpack.config.js"), 'w') as fle:
                fle.write(dedent("""
                    var webpack = require("webpack");

                    module.exports = {{
                      entry: [ "/modules/{0}.js" ],
                      output: {{
                        filename: "/compiled/dashboards/{0}.js",
                        library: "Dashboard"
                      }},
                      module: {{
                        loaders: [
                          {{
                            exclude: /node_modules/,
                            loader: "babel",
                            test: /\.jsx?$/,
                            query: {{
                                presets: ["react", "es2015"],
                                plugins: ["transform-object-rest-spread"]
                            }}
                          }},
                          {{
                            test: /\.css$/,
                            loader: "style!css?modules"
                          }}
                        ]
                      }},
                      plugins: [
                        new webpack.NoErrorsPlugin(),
                        new webpack.ProvidePlugin({{
                          Promise: 'imports?this=>global!exports?global.Promise!es6-promise',
                          fetch: 'imports?this=>global!exports?global.fetch!whatwg-fetch'
                        }})
                      ]
                    }};
                """.format(filename)))
            react_server.build_webpack(directory)
        finally:
            if directory and os.path.exists(directory):
                shutil.rmtree(directory)

    return final_location

