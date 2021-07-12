"""
gamgee/__init__.py


"""

import json
import functools as ft
import inspect as _inspect
from typing import Optional, Callable, Union, NoReturn

from . import auth
from . import args
from . import errors
from . import parsers
from . import types

__version__ = "0.3.2"


def sam(
    body: Optional[Union[bool,Callable]] = json.loads,
    pathParams: Optional[Union[bool,Callable]] = False,
    queryString: Optional[Union[bool,Callable]] = False,
    headers: Optional[Union[bool,Callable]] = False,
    authenticate: Optional[Callable[[dict], types.AuthUser]] = None,
    authorize: Optional[Callable[[types.AuthUser], bool]] = None,
    jsonize_response: bool = True,
    keep_event: bool = False,
    keep_context: bool = False,
    pass_auth_user: bool = True,
):
    """Wraps an AWS lambda handler function to handle auth, to catch
    and handle errors, and to convert lambda handler default parameters
    to a functions declared parameters.

    :param body: Should the wrapper function pass `event`'s "body"
        attribute as an arg to inner function (called "body")? If `body`
        is callable, it will be used to parse the values.

        For example, if the body is string-ified JSON, you can use `json.loads`
        to load the request (or `parsers.json`, a wrapper around `json.loads`).
        Or, you could use a `pydantic` model to parse and validate the input.

        If this param parsing raises an error, it will be caught and returned
        as an `errors.RequestParseError`.

        See also other params: `pathParams`, `queryString`, and `headers`.

    :param pathParams: Should the wrapper function pass `event`'s "pathParams"
        attribute as an arg to inner function (called "path")? If `pathParams`
        is callable, it will be used to parse the values.

        See also other params: `body`, `queryString`, and `headers`.

    :param queryString: Should the wrapper function pass `event`'s "queryString"
        attribute as an arg to inner function (called "query")? If `queryString`
        is callable, it will be used to parse the values.

        See also other params: `pathParams`, `body`, and `headers`.

    :param headers: Should the wrapper function pass `event`'s "headers"
        attribute as an arg to inner function (called "headers")? If `headers`
        is callable, it will be used to parse the values.

        See also other params: `pathParams`, `queryString`, and `body`.

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

    def wrapper(fn: Callable):

        # Get the function's return type, to use later when
        # deciding how to format response
        return_type = args.get_return_type(fn)

        @ft.wraps(fn)
        def inner(event: dict, context) -> dict:
            # Store function arguments
            kwargs = {}

            if authenticate is not None:
                # Authenticate the user
                try:
                    user = authenticate(event)
                except errors.HttpError as e:
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
            if body:
                try:
                    kwargs["body"] = body(event["body"]) if callable(body) else event["body"]
                except Exception as e:
                    return errors.RequestParseError().json(
                        f"Unable to read request body."
                    )
            if pathParams:
                try:
                    kwargs["path"] = pathParams(event["pathParameters"]) if callable(pathParams) \
                        else event["pathParameters"]
                except Exception as e:
                    return errors.RequestParseError().json(
                        f"Unable to read request path parameters."
                    )
            if queryString:
                try:
                    kwargs["query"] = queryString(event["queryStringParameters"]) if callable(queryString) \
                        else event["queryStringParameters"]
                except Exception as e:
                    return errors.RequestParseError().json(
                        f"Unable to read request query string parameters."
                    )
            if headers:
                try:
                    kwargs["headers"] = headers(event["headers"]) if callable(headers) else event["headers"]
                except Exception as e:
                    return errors.RequestParseError().json(
                        f"Unable to read request headers."
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
                print(f"UNCAUGHT ERROR: \"{e}\"")
                return errors.InternalServerError().json()

            # Return a response
            if jsonize_response:

                # If there isn't a return (as expected)
                # just return the success-ness
                if res is None and return_type in (None, NoReturn):
                    return {
                        "statusCode": 200,
                        "body": json.dumps({
                            "success": True,
                        })
                    }
                
                # If the response is a dict, merge
                # it with the `success`-ness flag
                if isinstance(res, dict):
                    return {
                        "statusCode": 200,
                        "body": json.dumps({
                            "success": True,
                            **res
                        })
                    }
                # Otherwise (if result isn't a dict)
                # return it as the value to key "result"
                return {
                    "statusCode": 200,
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
                    "statusCode": 200,
                    "body": res
                }
        return inner
    return wrapper

