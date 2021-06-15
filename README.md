# gamgee

[![Test Package](https://github.com/a-poor/gamgee/actions/workflows/test-package.yml/badge.svg?branch=main&event=push)](https://github.com/a-poor/gamgee/actions/workflows/test-package.yml)
[![PyPI](https://img.shields.io/pypi/v/gamgee)](https://pypi.org/project/gamgee)
[![PyPI - License](https://img.shields.io/pypi/l/gamgee)](https://pypi.org/project/gamgee)

_created by Austin Poor_

A python library for helping to setup an [AWS SAM](https://aws.amazon.com/serverless/sam) app.

## Quick Start

```python
In [1]: import gamgee                                                           

In [2]: @gamgee.sam() 
   ...: def lambda_handler(event: dict): 
   ...:     return [1,2,3] 
   ...:                                                                         

In [3]: lambda_handler(event={"body": ...}, context=None)                                     
Out[3]: {'status_code': 200, 'body': '{"success": true, "result": [1, 2, 3]}'}
```

## Installation

```bash
$ pip install gamgee
```


