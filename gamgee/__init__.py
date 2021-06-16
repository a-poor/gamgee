"""

## TODO:
* Capture / convert arguments / types
* If return type is None/NoReturn, don't return something
* Add multiple-dispatch switch to allow multiple HTTP methods

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

__version__ = "0.0.4"


def sam(
    method: Union[str,Method] = Method.GET,
    authenticate: Optional[Callable[[dict], AuthUser]] = None,
    authorize: Optional[Callable[[AuthUser], bool]] = None,
    jsonize_response: bool = True,
    keep_event: bool = False,
    keep_context: bool = False,
):
    """Wraps an AWS lambda handler function.

    If `authenticate` is not `None`, will pass 

    :param query_params: Should query params be passed
    :param path_params:
    :param unpack_body:
    :param packed_body:
    :param authenticate: Function to authenticate the requesting user.
    :param authorize: Function to authorize the requesting user.
    :param jsonize_response: Should the response body be wrapped in JSON?
    :param keep_event: Should the `event` dict be passed to the 
        wrapped function from AWS Lambda?
    :param keep_context: Should the `context` object be passed to the 
        wrapped function from AWS Lambda?
    """
    # Check authorize/authenticate
    if authorize is not None:
        assert authenticate is not None, "If `authorize` is not `None`, "+\
            "`authenticate` can't be `None`."

    # Coerce `method` to be a Method enum
    if not isinstance(method, Method):
        method = method.fromStr(str(method).upper())

    def wrapper(fn):

        fn_args = dict(_inspect.signature(fn).parameters)
        return_type = args.get_return_type(fn)

        if method is Method.GET:
            assumed_param_type = Query
        elif method is Method.POST:
            assumed_param_type = Body
        elif method is Method.PUT:
            assumed_param_type = Body
        elif method is Method.DELETE:
            assumed_param_type = Query
        else:
            assumed_param_type = Body

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
        def inner(event, context):
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

            # Get the correct args/kwargs
            kwargs = {}

            # Get the query/path/body/header params
            try:
                loc = "query params"
                for k, v in query_args.items():
                    key = v.key if v.key is not None else k
                    kwargs[k] = event["queryStringParameters"][key]
                
                loc = "path params"
                for k, v in path_args.items():
                    key = v.key if v.key is not None else k
                    kwargs[k] = event["pathParameters"][key]
                
                loc = "request body"
                for k, v in body_args.items():
                    key = v.key if v.key is not None else k
                    kwargs[k] = event[""][key]

                loc = "headers"
                for k, v in header_args.items():
                    key = v.key if v.key is not None else k
                    kwargs[k] = event.get("headers",{})[key]
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
                if authenticate is not None:
                    res = fn(**kwargs, authUser=user)
                else:
                    res = fn(**kwargs)
            except errors.HttpError as e:
                return e.json()
            except Exception as e:
                print("UNCAUGHT ERROR:", e)
                return errors.InternalServerError().json()

            # Return a response
            if jsonize_response:
                if res is None and return_type in (None, NoReturn):
                    return {
                        "status_code": 200,
                        "body": json.dumps({
                            "success": True,
                        })
                    }
                if isinstance(res, dict):
                    return {
                        "status_code": 200,
                        "body": json.dumps({
                            "success": True,
                            **res
                        })
                    }
                return {
                    "status_code": 200,
                    "body": json.dumps({
                        "success": True,
                        "result": res,
                    })
                }
            else:
                return {
                    "status_code": 200,
                    "body": res
                }
        return inner
    return wrapper


