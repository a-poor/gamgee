"""

## TODO:
* Capture / convert arguments / types
* If return type is None/NoReturn, don't return something
* Add multiple-dispatch switch to allow multiple HTTP methods

"""

import json
import functools as ft
from typing import Optional, Callable, Union

from . import auth
from . import args
from . import errors
from .types import AuthUser

__version__ = "0.0.4"


def sam(
    query_params: bool = True,
    path_params: bool = True,
    unpack_body: bool = True,
    packed_body: bool = False,
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

    def wrapper(fn):
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
            # TODO: ...
            kwargs = {"event": event}

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


            #TODO: If return type is None/NoReturn, don't include body? or just say success?

            # Return a response
            if jsonize_response:
                return {
                    "status_code": 200,
                    "body": json.dumps({
                        "success": True,
                        **({"result": res} if not isinstance(res, dict) else res)
                    })
                }
            else:
                return {
                    "status_code": 200,
                    "body": res
                }
        return inner
    return wrapper


