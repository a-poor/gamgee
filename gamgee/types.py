"""
gamgee/types.py

"""

from enum import Enum
from typing import NewType, Union, Optional, Any

from pydantic import BaseModel


AuthUser = Union[dict,BaseModel]

class RequestParam:
    """

    :param annotation: Argument's type annotation
    :param key: The value's key in the event `dict`
    """

    _name = "RequestParam"

    def __init__(self, annotation: type = Any, key: Optional[str] = None):
        self.annot = annotation
        self.key = key

    def __str__(self):
        return f"{self._name}[{self.annot}{('|'+str(self.key)) if self.key is not None else ''}]"
    
    def __repr__(self):
        return str(self)

    def to(self, T: 'RequestParam'):
        """Convert one `RequestParameter` subtype
        to another.

        :param T: A `RequestParam` subtype
        :returns: This value retyped as `T`
        """
        return T(self.annot, self.key)

class Path(RequestParam):
    _name = "Path"

class Query(RequestParam):
    _name = "Query"

class Body(RequestParam):
    _name = "Body"

class Header(RequestParam):
    _name = "Header"


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

