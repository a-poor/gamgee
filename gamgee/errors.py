"""
gamgee/errors.py

"""

import json
from typing import Optional


class BaseSamError(Exception):
    """Abstract base error for gamgee."""

class HttpError(BaseSamError):
    """

    """ 
    status_code: int = None
    default_message: str = None

    def json(self, message: Optional[str] = None):
        return {
            "status_code": self.status_code,
            "body": json.dumps({
                "success": False,
                "message": self.default_message if message is None else message
            })
        }


class RequestParseError(HttpError): 
    """

    """
    status_code = 400
    default_message = "Error parsing request."


class AuthenticationError(HttpError): 
    """

    """
    status_code = 401
    default_message = "Unable to authenticate."


class AuthorizationError(HttpError): 
    """

    """
    status_code = 403
    default_message = "Unauthorized."


class InternalServerError(HttpError): 
    """

    """
    status_code = 500
    default_message = "Internal server error."


class TypeCoersionError(InternalServerError, ValueError): 
    """

    """
    
    # def json(self, dtype: type, val_name: str = "value"):
    #     return super().json(f"Unable to convert `{val_name}` to `{dtype}`")

