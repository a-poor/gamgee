from enum import Enum
from typing import get_type_hints, Any, Callable, Union, Dict, Type

from pydantic import BaseModel


class RequestParam: pass

# TODO: Fill these in
class Path(RequestParam): pass
class Query(RequestParam): pass
class Body(RequestParam): pass


def get_args(fn: Callable) -> Dict[str, Type]:
    """Get a mapping from a function's arguments
    to it's response types.

    :param fn: Callable function with annotated argument types.
    """
    return {k: v for k, v in get_type_hints(fn) 
        if k != "return"}

def get_return_type(fn: Callable) -> Type:
    """Get the return type (if any) from the function `fn`.

    :param fn: Callable function to get return type from.
    """
    return get_type_hints(fn).get("return")

def coerce(t: Union[type, BaseModel], v: Any) -> Any: 
    raise NotImplementedError() #TODO

