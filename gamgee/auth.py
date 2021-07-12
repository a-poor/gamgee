"""
gamgee/auth.py

"""

import os
import datetime as dt
from typing import Optional, Callable

import jwt

from .errors import RequestParseError, AuthenticationError


DEFAULT_JWT_ALGO   = "HS256"
DEFAULT_JWT_SECRET = "secret"


def get_bearer_token(event: dict) -> str:
    """Get a bearer token from the request
    event.

    :param event: `event` dict passed to lambda function.
    :raises RequestParseError:
    :returns: Bearer token from request
    """
    try:
        return event["headers"]["Authorization"]
    except KeyError:
        raise RequestParseError()


def make_authorizer(secret: Optional[str] = None, algorithm: Optional[str] = None) -> Callable[[dict], dict]:
    """Create a JWT authorization function.

    :param secret: JWT secret for decoding incoming token.
        If not supplied, will check for the environment 
        variable: `JWT_SECRET`. If no environment variable, 
        will use `DEFAULT_JWT_SECRET`.
    :param algorithm: JWT encode/decode algorithm for decoding 
        incoming token. If not supplied, will check for the 
        environment variable: `JWT_ALGORITHM`. If no environment 
        variable, will use `DEFAULT_JWT_ALGORITHM`.
    :returns: Authorizer function
    """
    secret = secret if secret is not None else \
        os.environ.get("JWT_SECRET", DEFAULT_JWT_SECRET)
    algorithm = algorithm if algorithm is not None \
        else os.environ.get("JWT_ALGORITHM", DEFAULT_JWT_ALGO)

    def jwt_authorizer(event: dict) -> dict:
        """Authorize a JWT token from a lambda request event.

        :param event: Lambda request event
        :returns: Result of decoding the request's JWT token
        :raises RequestParseError: If JWT token can't be retreived
            from the request event (from `event.headers.Authorization`).
        :raises AuthenticationError: If the JWT token can't be validated.
        """
        token = get_bearer_token(event)
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]
        try:
            res = jwt.decode(token, secret, algorithms=[algorithm])
        except Exception as e: #TODO: Make less general
            raise AuthenticationError()
        return res
    return jwt_authorizer

