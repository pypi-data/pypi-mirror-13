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

"""Logic for storing and calling jsonrpc methods."""
from __future__ import absolute_import, division, print_function

import inspect
import json
import logging
import sys

import six
import wrapt
from werkzeug.debug.tbtools import get_current_traceback

import typedjsonrpc.parameter_checker as parameter_checker
from .errors import Error, InternalError, InvalidRequestError, MethodNotFoundError, ParseError
from .method_info import MethodInfo, MethodSignature

__all__ = ["Registry"]


def _get_default_logger():
    logger = logging.getLogger(__name__)
    if logger.getEffectiveLevel() == logging.NOTSET:
        logger.setLevel(logging.INFO)
    logger.handlers = [logging.StreamHandler(sys.stdout)]
    return logger


class Registry(object):
    """The registry for storing and calling jsonrpc methods.

    :attribute debug: Debug option which enables recording of tracebacks
    :type debug: bool
    :attribute tracebacks: Tracebacks for debugging
    :type tracebacks: dict[int, werkzeug.debug.tbtools.Traceback]

    .. versionadded:: 0.1.0
    """

    json_encoder = json.JSONEncoder()
    """The JSON encoder to use.  Defaults to :class:`json.JSONEncoder`

    .. versionadded:: 0.1.0
    .. versionchanged:: 0.2.0 Changed from class to instance
    """

    json_decoder = json.JSONDecoder()
    """The JSON decoder to use. Defaults to :class:`json.JSONDecoder`

    .. versionadded:: 0.1.0
    .. versionchanged:: 0.2.0 Changed from class to instance
    """

    def __init__(self,
                 debug=False,
                 strict_floats=True):
        """
        :param debug: If True, the registry records tracebacks for debugging purposes
        :type debug: bool
        :param strict_floats: If True, the registry does not allow ints as float parameters
        :type strict_floats: bool

        .. versionchanged:: 0.4.0 Added strict_floats option
        """
        self._name_to_method_info = {}
        self._register_describe()
        self.debug = debug
        self._strict_floats = strict_floats
        self._logger = _get_default_logger()
        self.tracebacks = {}

    def _register_describe(self):
        def _describe():
            return self.describe()
        _describe.__doc__ = self.describe.__doc__

        describe_signature = MethodSignature.create([], {}, dict)
        self.register("rpc.describe", _describe, describe_signature)

    def dispatch(self, request):
        """Takes a request and dispatches its data to a jsonrpc method.

        :param request: a werkzeug request with json data
        :type request: werkzeug.wrappers.Request
        :return: json output of the corresponding method
        :rtype: str

        .. versionadded:: 0.1.0
        """
        def _wrapped():
            messages = self._get_request_messages(request)
            results = [self._dispatch_and_handle_errors(message) for message in messages]
            non_notification_results = [x for x in results if x is not None]
            if len(non_notification_results) == 0:
                return None
            elif len(messages) == 1:
                return non_notification_results[0]
            else:
                return non_notification_results

        result, _ = self._handle_exceptions(_wrapped)
        if result is not None:
            return self._encode_complete_result(result)

    def _dispatch_and_handle_errors(self, msg):
        is_notification = isinstance(msg, dict) and "id" not in msg

        def _wrapped():
            result = self._dispatch_message(msg)
            if not is_notification:
                return Registry._create_result_response(msg["id"], result)

        result, _ = self._handle_exceptions(_wrapped, is_notification, self._get_id_if_known(msg))
        return result

    def _handle_exceptions(self, method, is_notification=False, msg_id=None):
        try:
            return method(), False
        except Error as exc:
            if not is_notification:
                if self.debug:
                    debug_url = self._store_traceback()
                    exc.data = {"message": exc.data, "debug_url": debug_url}
                return Registry._create_error_response(msg_id, exc), True
        except Exception as exc:  # pylint: disable=broad-except
            if not is_notification:
                exc_info = sys.exc_info()
                if self.debug:
                    debug_url = self._store_traceback()
                else:
                    debug_url = None
                exception_message = "id: {}, debug_url: {}".format(msg_id, debug_url)
                self._logger.exception(exception_message)
                new_error = InternalError.from_error(exc_info, self.json_encoder, debug_url)
                return Registry._create_error_response(msg_id, new_error), True

    def _encode_complete_result(self, result):
        if isinstance(result, list):
            return '[' + ','.join([self._encode_single_result(res) for res in result]) + ']'
        else:
            return self._encode_single_result(result)

    def _encode_single_result(self, result):
        msg_id = Registry._get_id_if_known(result)
        is_notification = msg_id is None

        def _encode():
            return self.json_encoder.encode(result)

        encoded, is_error = self._handle_exceptions(_encode,
                                                    is_notification=is_notification,
                                                    msg_id=msg_id)
        if is_error:
            # Fall back to default because previous encoding didn't work.
            return self.json_encoder.encode(encoded)
        else:
            return encoded

    def _store_traceback(self):
        traceback = get_current_traceback(skip=1,
                                          show_hidden_frames=False,
                                          ignore_system_exceptions=True)
        self.tracebacks[traceback.id] = traceback
        return "/debug/{}".format(traceback.id)

    @staticmethod
    def _get_id_if_known(msg):
        if isinstance(msg, dict) and "id" in msg:
            return msg["id"]
        else:
            return None

    def _dispatch_message(self, msg):
        self._check_request(msg)
        method = self._name_to_method_info[msg["method"]].method
        params = msg.get("params", [])
        parameter_checker.validate_params_match(method, params)
        if isinstance(params, list):
            result = method(*params)
        elif isinstance(params, dict):
            result = method(**params)
        else:
            raise InvalidRequestError("Given params '{}' are neither a list nor a dict."
                                      .format(msg["params"]))
        return result

    @staticmethod
    def _create_result_response(msg_id, result):
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result,
        }

    @staticmethod
    def _create_error_response(msg_id, exc):
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": exc.as_error_object(),
        }

    def register(self, name, method, method_signature=None):
        """Registers a method with a given name and signature.

        :param name: The name used to register the method
        :type name: str
        :param method: The method to register
        :type method: function
        :param method_signature: The method signature for the given function
        :type method_signature: MethodSignature | None

        .. versionadded:: 0.1.0
        """
        if inspect.ismethod(method):
            raise Exception("typedjsonrpc does not support making class methods into endpoints")
        self._name_to_method_info[name] = MethodInfo(name, method, method_signature)

    def method(self, returns, **parameter_types):
        """Syntactic sugar for registering a method

        Example:

            >>> registry = Registry()
            >>> @registry.method(returns=int, x=int, y=int)
            ... def add(x, y):
            ...     return x + y

        :param returns: The method's return type
        :type returns: type
        :param parameter_types: The types of the method's parameters
        :type parameter_types: dict[str, type]

        .. versionadded:: 0.1.0
        """
        @wrapt.decorator
        def type_check_wrapper(method, instance, args, kwargs):
            """Wraps a method so that it is type-checked.

            :param method: The method to wrap
            :type method: (T) -> U
            :return: The result of calling the method with the given parameters
            :rtype: U
            """
            if instance is not None:
                raise Exception("Instance shouldn't be set.")

            parameter_names = inspect.getargspec(method).args  # pylint: disable=deprecated-method
            defaults = inspect.getargspec(method).defaults  # pylint: disable=deprecated-method
            parameters = self._collect_parameters(parameter_names, args, kwargs, defaults)

            parameter_checker.check_types(parameters, parameter_types, self._strict_floats)

            result = method(*args, **kwargs)
            parameter_checker.check_return_type(result, returns, self._strict_floats)

            return result

        def register_method(method):
            """Registers a method with its fully qualified name.

            :param method: The method to register
            :type method: function
            :return: The original method wrapped into a type-checker
            :rtype: function
            """
            parameter_names = inspect.getargspec(method).args  # pylint: disable=deprecated-method
            parameter_checker.check_type_declaration(parameter_names, parameter_types)

            wrapped_method = type_check_wrapper(method, None, None, None)
            fully_qualified_name = "{}.{}".format(method.__module__, method.__name__)
            self.register(fully_qualified_name, wrapped_method,
                          MethodSignature.create(parameter_names, parameter_types, returns))
            return wrapped_method

        return register_method

    @staticmethod
    def _collect_parameters(parameter_names, args, kwargs, defaults):
        """Creates a dictionary mapping parameters names to their values in the method call.

        :param parameter_names: The method's parameter names
        :type parameter_names: list[string]
        :param args: *args passed into the method
        :type args: list[object]
        :param kwargs: **kwargs passed into the method
        :type kwargs: dict[string, object]
        :param defaults: The method's default values
        :type defaults: list[object]
        :return: Dictionary mapping parameter names to values
        :rtype: dict[string, object]
        """
        parameters = {}
        if defaults is not None:
            zipped_defaults = zip(reversed(parameter_names), reversed(defaults))
            for name, default in zipped_defaults:
                parameters[name] = default
        for name, value in zip(parameter_names, args):
            parameters[name] = value
        for name, value in kwargs.items():
            parameters[name] = value
        return parameters

    def describe(self):
        """Returns a description of all the methods in the registry.

        :return: Description
        :rtype: dict[str, object]

        .. versionadded:: 0.1.0
        """
        return {
            "methods": [method_info.describe()
                        for method_info in sorted(self._name_to_method_info.values())]
        }

    def _get_request_messages(self, request):
        """Parses the request as a json message.

        :param request: a werkzeug request with json data
        :type request: werkzeug.wrappers.Request
        :return: The parsed json object
        :rtype: dict[str, object]
        """
        data = request.get_data(as_text=True)
        try:
            msg = self.json_decoder.decode(data)
        except Exception:
            raise ParseError("Could not parse request data '{}'".format(data))
        if isinstance(msg, list):
            return msg
        else:
            return [msg]

    def _check_request(self, msg):
        """Checks that the request json is well-formed.

        :param msg: The request's json data
        :type msg: dict[str, object]
        """
        if "jsonrpc" not in msg:
            raise InvalidRequestError("'\"jsonrpc\": \"2.0\"' must be included.")
        if msg["jsonrpc"] != "2.0":
            raise InvalidRequestError("'jsonrpc' must be exactly the string '2.0', but it was '{}'."
                                      .format(msg["jsonrpc"]))
        if "method" not in msg:
            raise InvalidRequestError("No method specified.")
        if "id" in msg:
            if msg["id"] is None:
                raise InvalidRequestError("typedjsonrpc does not allow id to be None.")
            if isinstance(msg["id"], float):
                raise InvalidRequestError("typedjsonrpc does not support float ids.")
            if not isinstance(msg["id"], (six.string_types, six.integer_types)):
                raise InvalidRequestError("id must be a string or integer; '{}' is of type {}."
                                          .format(msg["id"], type(msg["id"])))
        if msg["method"] not in self._name_to_method_info:
            raise MethodNotFoundError("Could not find method '{}'.".format(msg["method"]))
