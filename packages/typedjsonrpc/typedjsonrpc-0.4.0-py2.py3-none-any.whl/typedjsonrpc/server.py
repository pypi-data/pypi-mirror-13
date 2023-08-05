# coding: utf-8
#
# Copyright 2015 Palantir Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contains the Werkzeug server for debugging and WSGI compatibility."""
from __future__ import absolute_import, division, print_function

from threading import Lock

from werkzeug.debug import DebuggedApplication
from werkzeug.exceptions import abort
from werkzeug.local import Local, LocalManager, LocalProxy
from werkzeug.routing import Map, Rule
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from .errors import get_status_code_from_error_code

__all__ = ["Server", "DebuggedJsonRpcApplication", "current_request"]


DEFAULT_API_ENDPOINT_NAME = "/api"

_CURRENT_REQUEST_KEY = "current_request"
_local = Local()  # pylint: disable=invalid-name
_LOCAL_MANAGER = LocalManager([_local])

current_request = LocalProxy(_local, _CURRENT_REQUEST_KEY)  # pylint: disable=invalid-name
"""A thread-local which stores the current request object when dispatching requests for
:class:`Server`.

Stores a :class:`werkzeug.wrappers.Request`.

.. versionadded:: 0.2.0
"""


class Server(object):
    """A basic WSGI-compatible server for typedjsonrpc endpoints.

    :attribute registry: The registry for this server
    :type registry: typedjsonrpc.registry.Registry

    .. versionadded:: 0.1.0
    .. versionchanged:: 0.4.0 Now returns HTTP status codes
    """

    def __init__(self, registry, endpoint=DEFAULT_API_ENDPOINT_NAME):
        """
        :param registry: The JSON-RPC registry to use
        :type registry: typedjsonrpc.registry.Registry
        :param endpoint: The endpoint to publish JSON-RPC endpoints. Default "/api".
        :type endpoint: str
        """
        self.registry = registry
        self._endpoint = endpoint
        self._url_map = Map([Rule(endpoint, endpoint=self._endpoint)])

        self._before_first_request_funcs = []

        self._after_first_request_handled = False
        self._before_first_request_lock = Lock()

    def _dispatch_request(self, request):
        self._try_trigger_before_first_request_funcs()
        adapter = self._url_map.bind_to_environ(request.environ)
        endpoint, _ = adapter.match()
        if endpoint == self._endpoint:
            return self._dispatch_jsonrpc_request(request)
        else:
            abort(404)

    def _dispatch_jsonrpc_request(self, request):
        json_output = self.registry.dispatch(request)
        if json_output is None:
            return Response(status=204)
        return Response(json_output,
                        mimetype="application/json",
                        status=self._determine_status_code(json_output))

    def _determine_status_code(self, json_output):
        output = self.registry.json_decoder.decode(json_output)
        if isinstance(output, list) or "result" in output:
            return 200
        else:
            assert "error" in output, "JSON-RPC is malformed and doesn't contain result or error"
            return get_status_code_from_error_code(output["error"]["code"])

    def wsgi_app(self, environ, start_response):
        """A basic WSGI app"""
        @_LOCAL_MANAGER.middleware
        def _wrapped_app(environ, start_response):
            request = Request(environ)
            setattr(_local, _CURRENT_REQUEST_KEY, request)
            response = self._dispatch_request(request)
            return response(environ, start_response)
        return _wrapped_app(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def run(self, host, port, **options):
        """For debugging purposes, you can run this as a standalone server.

        .. WARNING:: **Security vulnerability**

            This uses :class:`DebuggedJsonRpcApplication` to assist debugging. If you want to use
            this in production, you should run :class:`Server` as a standard WSGI app with
            `uWSGI <https://uwsgi-docs.readthedocs.org/en/latest/>`_ or another similar WSGI server.

        .. versionadded:: 0.1.0
        """
        self.registry.debug = True
        debugged = DebuggedJsonRpcApplication(self, evalex=True)
        run_simple(host, port, debugged, use_reloader=True, **options)

    def _try_trigger_before_first_request_funcs(self):  # pylint: disable=C0103
        """Runs each function from ``self.before_first_request_funcs`` once and only once."""
        if self._after_first_request_handled:
            return
        else:
            with self._before_first_request_lock:
                if self._after_first_request_handled:
                    return
                for func in self._before_first_request_funcs:
                    func()
                self._after_first_request_handled = True

    def register_before_first_request(self, func):
        """Registers a function to be called once before the first served request.

        :param func: Function called
        :type func: () -> object

        .. versionadded:: 0.1.0
        """
        self._before_first_request_funcs.append(func)


class DebuggedJsonRpcApplication(DebuggedApplication):
    """A JSON-RPC-specific debugged application.

    This differs from DebuggedApplication since the normal debugger assumes you
    are hitting the endpoint from a web browser.

    A returned response will be JSON of the form: ``{"traceback_id": <id>}`` which
    you can use to hit the endpoint ``http://<host>:<port>/debug/<traceback_id>``.

    .. versionadded:: 0.1.0

    .. WARNING:: **Security vulnerability**

        This should never be used in production because users have arbitrary shell
        access in debug mode.
    """
    def __init__(self, app, **kwargs):
        """
        :param app: The wsgi application to be debugged
        :type app: typedjsonrpc.server.Server
        :param kwargs: The arguments to pass to the DebuggedApplication
        """
        super(DebuggedJsonRpcApplication, self).__init__(app, **kwargs)
        self._debug_map = Map([Rule("/debug/<int:traceback_id>", endpoint="debug")])

    def debug_application(self, environ, start_response):
        """Run the application and preserve the traceback frames.

        :param environ: The environment which is passed into the wsgi application
        :type environ: dict[str, object]
        :param start_response: The start_response function of the wsgi application
        :type start_response: (str, list[(str, str)]) -> None
        :rtype: generator[str]

        .. versionadded:: 0.1.0
        """
        adapter = self._debug_map.bind_to_environ(environ)
        if adapter.test():
            _, args = adapter.match()
            return self.handle_debug(environ, start_response, args["traceback_id"])
        else:
            return super(DebuggedJsonRpcApplication, self).debug_application(environ,
                                                                             start_response)

    def handle_debug(self, environ, start_response, traceback_id):
        """Handles the debug endpoint for inspecting previous errors.

        :param environ: The environment which is passed into the wsgi application
        :type environ: dict[str, object]
        :param start_response: The start_response function of the wsgi application
        :type start_response: (str, list[(str, str)]) -> NoneType
        :param traceback_id: The id of the traceback to inspect
        :type traceback_id: int

        .. versionadded:: 0.1.0
        """
        if traceback_id not in self.app.registry.tracebacks:
            abort(404)
        self._copy_over_traceback(traceback_id)
        traceback = self.tracebacks[traceback_id]
        rendered = traceback.render_full(evalex=self.evalex, secret=self.secret)
        response = Response(rendered.encode('utf-8', 'replace'),
                            headers=[('Content-Type', 'text/html; charset=utf-8'),
                                     ('X-XSS-Protection', '0')])
        return response(environ, start_response)

    def _copy_over_traceback(self, traceback_id):
        if traceback_id not in self.tracebacks:
            traceback = self.app.registry.tracebacks[traceback_id]
            self.tracebacks[traceback_id] = traceback
            for frame in traceback.frames:
                self.frames[frame.id] = frame
