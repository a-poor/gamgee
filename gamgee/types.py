"""
gamgee/types.py

"""

from enum import Enum
from typing import Union
from pydantic import BaseModel


AuthUser = Union[dict,BaseModel]


class Method(Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"

    @classmethod
    def fromStr(cls, method: str):
        if method == "GET":
            return cls.GET
        if method == "PUT":
            return cls.PUT
        if method == "POST":
            return cls.POST
        if method == "DELETE":
            return cls.DELETE
        vals = {"GET", "POST", "PUT", "DELETE"}
        raise ValueError(
            f"Unknown HTTP method '{method}' allowed values are: {vals}"
        )

