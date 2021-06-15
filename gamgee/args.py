from enum import Enum
from typing import get_type_hints, Any, Callable, Union, _SpecialGenericAlias

from pydantic import BaseModel


class RequestParam: pass

# TODO: Fill these in
class Path(RequestParam): pass
class Query(RequestParam): pass
class Body(RequestParam): pass


def get_args(fn: Callable):
    return {k: v for k, v in get_type_hints(fn) 
        if k != "return"}


def coerce(t: Union[type, BaseModel], v: Any) -> Any: 
    raise NotImplementedError() #TODO

