# gamgee

[![Test Package](https://github.com/a-poor/gamgee/actions/workflows/test-package.yml/badge.svg?branch=main&event=push)](https://github.com/a-poor/gamgee/actions/workflows/test-package.yml)
[![PyPI](https://img.shields.io/pypi/v/gamgee)](https://pypi.org/project/gamgee)
[![PyPI - License](https://img.shields.io/pypi/l/gamgee)](https://pypi.org/project/gamgee)

A python library for helping to setup an [AWS SAM](https://aws.amazon.com/serverless/sam) app -- specifically API Gateway SAM apps. `gamgee` aims to help users avoid rewriting boilerplate code within AWS Lambda handler functions. 

The core functionality is wrapped up in the decorator function `@gamgee.sam` -- which can help with: 
* Converting API request `event` dictionaries to function params (gathered from path-params, the query string, and the request body)
* Handling errors and responses by catching them and returning them with the propper HTTP status codes
* Authenticating / authorizing users making requests

## Quick Start

```python
In [1]: import gamgee                                                           

In [2]: event = {"queryStringParameters": {"name": "samwise"}}                  

In [3]: @gamgee.sam() 
   ...: def lambda_handler(name: gamgee.Query(str)) -> int: 
   ...:     return len(name) 
   ...:                                                                         

In [4]: lambda_handler(event, None)                                             
Out[4]: {'status_code': 200, 'body': '{"success": true, "result": 7}'}
```

## Installation

```bash
$ pip install gamgee
```

## To-Do

- [ ] Handle function request type parsing like [FastAPI](https://fastapi.tiangolo.com/)

