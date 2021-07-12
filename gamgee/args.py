"""
gamgee/args.py

"""

from enum import Enum
from typing import get_type_hints, Callable, Dict, Type, NoReturn


def get_return_type(fn: Callable) -> Type:
    """Get the return type (if any) from the function `fn`.

    :param fn: Callable function to get return type from.
    """
    return get_type_hints(fn).get("return")

