
import json as _json
from typing import Union, TypeVar


T = TypeVar("T")


def identity(x: T) -> T:
    return x

def parse_json(s: str) -> Union[dict,list,str,int,float]:
    return _json.loads(s)




