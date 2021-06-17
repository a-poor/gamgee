"""
gamgee/args.py

"""

from enum import Enum
from typing import get_type_hints, Callable, Dict, Type, NoReturn




def is_optional(t: Type) -> bool:
    """Check if a type annotation is `Optional`.

    :param t: The type annotation
    :returns: Type's optional-ness
    """
    if t.__module__ != "Typing": return False
    if not hasattr(t,"__args__"): return False
    args = t.__args__
    if len(args) != 2: return False
    if type(None) not in args: return False
    return True

def get_opt_type(t: Type) -> Type:
    assert is_optional(t), "`t` isn't an Optional type"
    return t.__args__[0]

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

def returns_null(fn: Callable) -> bool:
    return get_return_type(fn) in (None, NoReturn)

