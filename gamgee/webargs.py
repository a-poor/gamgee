import json
import functools as ft
from typing import Optional, Callable, Any, Dict, List

import webargs
from pydantic import BaseModel

class SAMEventIdentity(BaseModel):
    """
    """
    cognitoIdentityPoolId: Optional[Any] = None
    accountId: Optional[Any] = None
    cognitoIdentityId: Optional[Any] = None
    caller: Optional[Any] = None
    accessKey: Optional[Any] = None
    sourceIp: Optional[Any] = None
    cognitoAuthenticationType: Optional[Any] = None
    cognitoAuthenticationProvider: Optional[Any] = None
    userArn: Optional[Any] = None
    userAgent: Optional[Any] = None
    user: Optional[Any] = None


class SAMEventRequestContext(BaseModel):
    """
    """
    accountId: Optional[str] = None
    resourceId: Optional[str] = None
    stage: Optional[str] = None
    requestTime: Optional[str] = None
    requestTimeEpoch: Optional[str] = None
    identity: Optional[SAMEventIdentity] = None


class SAMEvent(BaseModel):
    """
    """
    body: str
    resource: str
    httpMethod: str
    isBase64Encoded: bool
    queryStringParameters: Optional[Dict[str, Any]] = None
    multiValueQueryStringParameters: Optional[Dict[str, List[Any]]] = None
    pathParameters: Optional[Dict[str, Any]] = None
    stageVariables: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    multiValueHeaders: Optional[Dict[str, List[Any]]] = None
    requestContext: Optional[SAMEventRequestContext] = None


def sam():
    """
    """

    def wrapper(fn: Callable):


        @ft.wraps(fn)
        def inner(event: Dict[str, Any], context: Any):
            sam_event = SAMEvent(**event)
            
        return inner
    return wrapper


