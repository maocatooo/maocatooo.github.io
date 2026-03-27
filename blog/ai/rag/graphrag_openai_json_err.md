---
title: AI解决不了的问题之 graphrag 使用 openai sdk 出现 "We could not parse the JSON body of your request"
date: 2026-03-27 17:45:42
tags: [graphrag, openai]
---

参考资料：

https://github.com/microsoft/graphrag/issues/2286   
https://community.openai.com/t/solved-error-we-could-not-parse-the-json-body-of-your-request/545372 

最近被安排去调查 graphrag index 失败的问题

公司的一个产品在 rag 功能为客户提供了 graphrag 选项把用户数据通过 graphrag 去聚合
```shell
graphrag index --root  /data/xxx/xx
```

然而在大量训练时，经常出现 
```shell
openai.BadRequestError: Error code: 400 - {'error': {'message': "We could not parse the JSON body of your request. (HINT: This likely means you aren't using your HTTP library correctly. The OpenAI API expects a JSON payload, but what was sent was not valid JSON. If you have trouble figuring out how to fix this, please contact us through our help center at help.openai.com.)", 'type': 'invalid_request_error', 'param': None, 'code': None}}
```
问GPT, 一堆说什么调用不准确，上网一搜，都是有前因没结果的  

训练错误的文件拿下来单独跑一下流程，又是好的

追了一下源代码，graphrag 底层还是用了 openai 官方的 sdk，所有的请求都是 openai sdk 自己发送出去的，也就是说他服务端自己不能理解自己的请求入参  
一脸懵，没办法，只能自己改了  

不侵入源码的情况下添加了两个改动项目，提升鲁棒性     
1. 为 openai._base_client 添加 debug 日志，直接输出请求的入参，方便具体看到每次的入参情况
2. 添加 graphrag 调用 openai sdk 时的重试情况，把 400 code 接入到重试里  

源graphrag cli代码   

```python
from graphrag.cli.main import app

app(prog_name="graphrag")
```

改动： 
```python
# training.py
import os.path

from fnllm.openai.llm.services.retryer import OPENAI_RETRYABLE_ERRORS
from openai import BadRequestError

OPENAI_RETRYABLE_ERRORS.append(BadRequestError)

from graphrag.cli.main import app
import logging

logger = logging.getLogger("openai._base_client")
logger.setLevel(logging.DEBUG)

OPENAI_BASE_CLIENT_LOG_DIR = "/data/log"

if OPENAI_BASE_CLIENT_LOG_DIR:
    os.makedirs(OPENAI_BASE_CLIENT_LOG_DIR, exist_ok=True)

file_handler = logging.FileHandler(os.path.join(OPENAI_BASE_CLIENT_LOG_DIR, "openai_base_client.log"), encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# """
# python3.12 training.py index --root /data/xxx/xxx
# python3.12 training.py query --method local --query  "讲一下罗永浩和西贝发生的事" --root /data/xxx/xxx
# python3.12 training.py update --root /data/xxx/xxx
# """
app(prog_name="graphrag")

```