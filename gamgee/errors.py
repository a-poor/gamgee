import json
from typing import Optional

class SamError(Exception): pass


class HttpError(SamError): 
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
    status_code = 400
    default_message = "Error parsing request."


class AuthenticationError(HttpError): 
    status_code = 401
    default_message = "Unable to authenticate."


class AuthorizationError(HttpError): 
    status_code = 403
    default_message = "Unauthorized."


