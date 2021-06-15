import json
from enum import Enum
import functools as ft
from typing import NewType, Optional, Callable

from pydantic import BaseModel

from . import errors


AuthUser = NewType("AuthUser", BaseModel)

class Methods(Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"


def sam(
    authenticate: Optional[Callable[[dict], AuthUser]] = None,
    authorize: Optional[Callable[[AuthUser], bool]] = None,
    jsonize_response: bool = True,
):
    """

    :param jsonize_response:
    :param authenticate:
    :param authorize:
    """
    if authorize is not None:
        assert authenticate is not None, "If `authorize` is not `None`, `authenticate` can't be `None`."

    def wrapper(fn):
        @ft.wraps(fn)
        def inner(event, context):
            # Authenticate the user
            try:
                user = authenticate(event)
            except errors.HttpError as e: #TODO: Make less general
                return e.json()
            
            # Authorize the user
            try:
                if not authorize(user):
                    raise errors.AuthorizationError()
            except errors.HttpError as e:
                return e.json()

            # Get the correct args/kwargs
            # TODO: ...
            kwargs = {}

            # Call the function
            if authenticate is not None:
                res = fn(**kwargs, auth_user=user)
            else:
                res = fn(**kwargs)

            # Return a response
            if jsonize_response:
                return {
                    "status_code": 200,
                    "body": json.dumps({
                        "success": True,
                        **({"result": res} if isinstance(res, dict) else res)
                    })
                }
            else:
                return {
                    "status_code": 200,
                    "body": res
                }
        return inner
    return wrapper


