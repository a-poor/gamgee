"""
gamgee/args.py

"""

import re
from enum import Enum
import typing
from typing import get_type_hints, Any, Callable, Union, Dict, Type, NoReturn, List

from pydantic import BaseModel

from . import errors


ALLOWED_COLLECTION_TYPES = (
    "List",
    "Dict",
    "Tuple",
    "Set",
)
ALLOWED_TYPES = (
    *ALLOWED_COLLECTION_TYPES,
    "Any",
    "Union",
    # "Optional",
    # "NoReturn",
)


def to_snake(name: str) -> str:
    """Make a `dict` key safe to act as a variable name.

    :param name: Dict key to make variable-name-safe
    :returns: Cleaned, snake-case version of `name`
    """
    # If name is a blank string, use an underscore instead
    if len(name) == 0: return "_"
    # Replace spaces and hyphens with underscores
    clean = re.sub(r"[ -]","_",name.strip())
    # Replace non-alphanumeric characters with underscores
    clean = re.sub(r"[^A-Za-z0-9_]","_",clean)
    # If `name` starts with a number, add a leading underscores
    if clean[0] in "0123456789": clean = "_"+clean
    return clean


def get_args(fn: Callable) -> Dict[str, Type]:
    """Get a mapping from a function's arguments
    to it's response types.

    :param fn: Callable function with annotated argument types.
    :returns: A mapping from argument name to argument type
    """
    return {k: v for k, v in get_type_hints(fn) 
        if k != "return"}

def get_return_type(fn: Callable) -> Type:
    """Get the return type (if any) from the function `fn`.

    :param fn: Callable function to get return type from.
    """
    return get_type_hints(fn).get("return")

def coerce(t: Union[type, BaseModel], v: Any) -> Any:
    """Attempts to convert value `v` to type `t`.

    :param t: Type to convert `v` to.
    :param v: Value to convert to type `t`.
    :returns: `v` coerced to type `t`
    :raises ValueError: 
    """

    raise NotImplementedError() #TODO:

    # Is the type from (allowed subset of) the `typing` library
    if hasattr(t, "_name") and t._name in ALLOWED_TYPES:
        if t is typing.Any: return v


    if isinstance(t, (type, BaseModel)):
        try:
            return t(v)
        except Exception as e:
            raise errors.TypeCoersionError(f"Unable to parse value as {t}") from e

def returns_null(fn: Callable) -> bool:
    return get_return_type(fn) in (None, NoReturn)

