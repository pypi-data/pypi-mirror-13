import pprint
import jsonschema
import logging
from importlib import import_module
from flask import request, jsonify
from flask.ext.cors import cross_origin
from klue.exceptions import KlueException, ValidationError, InternalServerError
from bravado_core.operation import Operation
from bravado_core.param import unmarshal_param
from bravado_core.request import IncomingRequest, unmarshal_request


log = logging.getLogger(__name__)


def get_function(pkgpath):
    """Take a full path to a python method, for example mypkg.subpkg.method and
    return the method (after importing the required packages)
    """
    # Extract the module and function name from pkgpath
    elems = pkgpath.split('.')
    if len(elems) <= 1:
        raise Exception("Path %s is too short. Should be at least module.func." % elems)
    func_name = elems[-1]
    func_module = '.'.join(elems[0:-1])

    # Load the function's module and get the function
    try:
        m = import_module(func_module)
        f = getattr(m, func_name)
        return f
    except Exception as e:
        raise Exception("Failed to import %s: " % pkgpath + str(e))


# TODO: add authentication when relevant
# TODO: support in-query parameters
def spawn_server_api(app, api_spec):
    """Take a a Flask app and a swagger file in YAML format describing a REST
    API, and populate the app with routes handling all the paths and methods
    declared in the swagger file.

    Also handle marshaling and unmarshaling between json and object instances
    representing the definitions from the swagger file.
    """

    def mycallback(endpoint):
        handler_func = get_function(endpoint.handler_server)

        # Generate api endpoint around that handler
        handler_wrapper = _generate_handler_wrapper(api_spec, endpoint, handler_func)

        # Bind handler to the API path
        log.info("Binding %s %s ==> %s" % (endpoint.method, endpoint.path, endpoint.handler_server))
        endpoint_name = endpoint.path.replace('/', '_')
        app.add_url_rule(endpoint.path, endpoint_name, handler_wrapper, methods=[endpoint.method])


    api_spec.call_on_each_endpoint(mycallback)


def _generate_handler_wrapper(api_spec, endpoint, handler_func):
    """Generate a handler method for the given url method+path and operation"""

    # Decorate the handler function, if Swagger spec tells us to
    if endpoint.decorate_server:
        decorator = get_function(endpoint.decorate_server)
        handler_func = decorator(handler_func)

    def handler_wrapper():
        log.info("Calling %s" % handler_func.__name__)

        req = FlaskRequestProxy(request)

        try:
            # Note: unmarshall validates parameters but does not fail
            # if extra unknown parameters are submitted
            parameters = unmarshal_request(req, endpoint.operation)
            # Example of parameters: {'body': RegisterCredentials()}
        except jsonschema.exceptions.ValidationError as e:
            new_e = ValidationError(str(e))
            return new_e.http_reply()

        if endpoint.param_in_body:
            assert len(parameters) == 1
            values = list(parameters.values())
            result = handler_func(values[0])
        elif endpoint.param_in_query:
            result = handler_func(**parameters)
        elif endpoint.no_params:
            result = handler_func()
        else:
            raise Exception("WTF? expected parameters are neither in query nor in body.")

        if not result:
            return InternalServerError("Have nothing to send in response").http_reply()

        if not hasattr(result, '__module__') or not hasattr(result, '__class__'):
            return InternalServerError("Method %s did not return a class instance but a %s" %
                                       (endpoint.handler_server, type(result))).http_reply()

        result_type = result.__module__ + "." + result.__class__.__name__
        if result_type == 'flask.wrappers.Response':
            # Already a flask Response. No need to marshal
            return result

        # TODO: check that result is an instance of a model expected as response from this endpoint
        result_json = api_spec.model_to_json(result)

        # Send a Flask Response with code 200 and result_json
        r = jsonify(result_json)
        r.status_code = 200
        return r


    handler_wrapper = cross_origin(headers=['Content-Type', 'Authorization'])(handler_wrapper)
    return handler_wrapper


class FlaskRequestProxy(IncomingRequest):
    """Take a flask.request object and make it look like a
    bravado_core.request.IncomingRequest"""

    path = None
    query = None
    form = None
    headers = None
    files = None

    def __init__(self, request):
        self.request = request
        print("request: " + pprint.pformat(request.args))
        self.query = request.args

    def json(self):
        # Convert a weltkreuz ImmutableDict to a simple python dict
        j = self.request.form.copy().to_dict()
        log.info("json is: " + pprint.pformat(j))
        return j
