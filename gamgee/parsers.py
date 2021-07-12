
import json as _json
from typing import Union, TypeVar


T = TypeVar("T")


def identity(x: T) -> T:
    """The identity function `f(x) = x`.
    """
    return x

def parse_json(s: str) -> Union[dict,list,str,int,float]:
    """A wrapper around `json.loads`.
    """
    return _json.loads(s)




