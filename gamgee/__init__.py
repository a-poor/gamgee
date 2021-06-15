"""

## TODO:
* Capture / convert arguments / types
* If return type is None/NoReturn, don't return something


"""

import json
from enum import Enum
import functools as ft
from typing import NewType, Optional, Callable

from pydantic import BaseModel

from . import auth
from . import args
from . import errors

__version__ = "0.0.4"


AuthUser = NewType("AuthUser", BaseModel)

class Method(Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"


def sam(
    method: Method = Method.GET,
    authenticate: Optional[Callable[[dict], AuthUser]] = None,
    authorize: Optional[Callable[[AuthUser], bool]] = None,
    jsonize_response: bool = True,
):
    """Wraps an AWS lambda handler function.

    :param method: (NOTE: Unused for now) The request's HTTP method 
    :param authenticate: Function to authenticate the requesting user.
    :param authorize: Function to authorize the requesting user.
    :param jsonize_response: Should the response body be wrapped in JSON?
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
                    res = fn(**kwargs, auth_user=user)
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


