"""
gamgee/__init__.py


"""

import json
import functools as ft
import inspect as _inspect
from typing import Optional, Callable, Union, NoReturn, Any

from . import auth
from . import args
from . import errors
from . import types
from .types import AuthUser, Method, Path, Body, Query, Header, RequestParam

__version__ = "0.1.0"


def sam(
    method: Union[str,Method] = Method.GET,
    authenticate: Optional[Callable[[dict], AuthUser]] = None,
    authorize: Optional[Callable[[AuthUser], bool]] = None,
    jsonize_response: bool = True,
    keep_event: bool = False,
    keep_context: bool = False,
    pass_auth_user: bool = True,
):
    """Wraps an AWS lambda handler function to handle auth, to catch
    and handle errors, and to convert lambda handler default parameters
    to a functions declared parameters.

    :param method: HTTP method for request.

        Note: `method` parameter is used to determine where to look for
        parameter arguments (if the location isn't already specified).
        POST and PUT methods look for arguments in the body, while 
        GET and DELETE look in the query string.
    :param authenticate: Function to authenticate the requesting user.
        Takes the full `event` as an input and returns a User.
    :param authorize: Function to authorize the requesting user.
        Note: `authenticate` must also be present.
    :param jsonize_response: Should the response body be wrapped in JSON?
        If so, the response's body will be a string-ified json dict
        of the following form: `{"success": true, "result": ...}`

        If `jsonize_response` is `True` but the function's signature
        shows a return value of `None` or `NoReturn`, and the function 
        does in fact return `None`, the body will not have a "result"
        attribute, only "success".

        If `jsonize_response` is `True` and the returned value is a dict,
        that value will be merged with a dict: `{"success": True}`
    :param keep_event: Should the `event` dict be passed to the 
        wrapped function from AWS Lambda?
    :param keep_context: Should the `context` object be passed to the 
        wrapped function from AWS Lambda?
    :param pass_auth_user: If authentication function supplied,
        should `authUser` be passed as a kwarg to the wrapped function?

    :returns: Decorated lambda handler function
    """
    # Check authorize/authenticate
    if authorize is not None:
        assert authenticate is not None, "If `authorize` is not `None`, "+\
            "`authenticate` can't be `None`."

    # Coerce `method` to be a Method enum
    if not isinstance(method, Method):
        method = method.fromStr(str(method).upper())

    def wrapper(fn: Callable):

        # Get the function's arguments
        fn_args = dict(_inspect.signature(fn).parameters)
        return_type = args.get_return_type(fn)

        # Assume where to find unspecified args
        # based on request method
        if method is Method.GET:
            assumed_param_type = Query
        elif method is Method.POST:
            assumed_param_type = Body
        elif method is Method.PUT:
            assumed_param_type = Body
        elif method is Method.DELETE:
            assumed_param_type = Query
        else:
            assumed_param_type = Query

        # Get function arguments and matching annotations
        # if a `RequestParam` type isn't set, use `assumed_param_type`
        # based on the HTTP method
        fn_args = {
            k: (
                (v.annotation if v.annotation is not _inspect._empty else Any)
                if isinstance(v.annotation, RequestParam) else 
                assumed_param_type(v.annotation))
            for k, v in fn_args.items()
        }

        # Divide arguments out according to their source locations
        query_args = {k: v for k, v in fn_args.items() if isinstance(v, Query)}
        path_args = {k: v for k, v in fn_args.items() if isinstance(v, Path)}
        body_args = {k: v for k, v in fn_args.items() if isinstance(v, Body)}
        header_args = {k: v for k, v in fn_args.items() if isinstance(v, Header)}

        @ft.wraps(fn)
        def inner(event: dict, context) -> dict:
            # Store function arguments
            kwargs = {}

            if authenticate is not None:
                # Authenticate the user
                try:
                    user = authenticate(event)
                except errors.HttpError as e: #TODO: Make less general
                    return e.json()

                if authorize is not None:
                    # Authorize the user
                    try:
                        if not authorize(user):
                            raise errors.AuthorizationError()
                    except errors.HttpError as e:
                        return e.json()
                
                # Does the user want the authorized
                # user as an argument?
                if pass_auth_user:
                    kwargs["authUser"] = user


            # Get the query/path/body/header params
            try:
                loc = "query params"
                for k, v in query_args.items():
                    key = v.key if v.key is not None else k
                    kwargs[k] = event.get("queryStringParameters", {})[key]
                
                loc = "path params"
                for k, v in path_args.items():
                    key = v.key if v.key is not None else k
                    kwargs[k] = event.get("pathParameters", {})[key]
                
                loc = "request body"
                for k, v in body_args.items():
                    key = v.key if v.key is not None else k
                    kwargs[k] = event.get("body", {})[key]

                loc = "headers"
                for k, v in header_args.items():
                    key = v.key if v.key is not None else k
                    kwargs[k] = event.get("headers", {})[key]
            except Exception as e:
                return errors.RequestParseError().json(
                    f"Couldn't read parameter {k} from {loc}"
                )
            
            # Add event/context if requested
            if keep_event:
                kwargs["event"] = event
            if keep_context:
                kwargs["context"] = context

            # Call the function
            try:
                res = fn(**kwargs)
            except errors.HttpError as e:
                return e.json()
            except Exception as e:
                print("UNCAUGHT ERROR:", e)
                return errors.InternalServerError().json()

            # Return a response
            if jsonize_response:

                # If there isn't a return (as expected)
                # just return the success-ness
                if res is None and return_type in (None, NoReturn):
                    return {
                        "status_code": 200,
                        "body": json.dumps({
                            "success": True,
                        })
                    }
                
                # If the response is a dict, merge
                # it with the `success`-ness flag
                if isinstance(res, dict):
                    return {
                        "status_code": 200,
                        "body": json.dumps({
                            "success": True,
                            **res
                        })
                    }
                # Otherwise (if result isn't a dict)
                # return it as the value to key "result"
                return {
                    "status_code": 200,
                    "body": json.dumps({
                        "success": True,
                        "result": res,
                    })
                }
            else:
                # If not json-izing the response, pass
                # it as the value to the key "body"
                # (still with a status-code of 200)
                return {
                    "status_code": 200,
                    "body": res
                }
        return inner
    return wrapper

