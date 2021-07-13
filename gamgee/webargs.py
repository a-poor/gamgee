import json
import functools as ft
from typing import Optional, Callable

import webargs


def sam(args=...):
    """
    """
    def wrapper(fn: Callable):
        @ft.wraps(fn)
        def inner(event, context):
            pass
        return inner
    return wrapper


