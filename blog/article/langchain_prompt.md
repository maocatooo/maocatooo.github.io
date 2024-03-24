---
title: "使用 langchain 做一个 prompt 工程师 🙈" 
date: 2023-08-01
tags: [langchain, prompt, AI]
#hide: true
#hidden: true
---

[langchain](https://github.com/langchain-ai/langchain)是一个开发由语言模型驱动的应用程序的框架,简单来说就是将LMM打包层应用层面的封装,使普通开发者(比如我)也能开发AI相关的应用

我能想到的相关应用：

1. 聊天机器人
2. 知识文档问答库(AI客服) [Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat)
3. 构建NLP应用程序
4. ...

如果你使用过 ChatGPT 就会发现 GPT 回答问题的时候就会多说一些前后缀相关无用的东西,使用 langchain 的 **prompt template** 就能非常方便的避免掉这个问题

一个示例, 使用 ExampleSelector 和 PromptTemplate 做提示返回模板

```python
from langchain.llms import OpenAI
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import FewShotPromptTemplate, PromptTemplate

openai_api_key = "{{you_openai_api_key}}"
llm: OpenAI = OpenAI(
    openai_proxy="127.0.0.1:4780", ## 这里是代理，你懂的
    openai_api_key=openai_api_key)

response_schemas = [
    ResponseSchema(name="user_input", description="这是用户的输入"),
    ResponseSchema(name="date", description="这是通过用户的输入得到的时间")
]

outputParser = StructuredOutputParser.from_response_schemas(response_schemas)

template = """

示例输入:
{user_input}
示例输出:
{output}
"""

example_prompt = PromptTemplate(
    template=template,
    input_variables=["user_input", "output"],
)

examples = [
    {"user_input": "今天是2023-08-01,今天吃米饭用了10元",
     "output": """date:2023-08-01,amount:10, user_input:昨天早上吃米饭用了10元"""},
    {"user_input": "今天是2023-08-02,昨天早上吃米饭用了10.1元",
     "output": """date:2023-08-01,amount:10.1, user_input:昨天早上吃米饭用了10元"""},
    {"user_input": "今天是2023-08-03,前天早上吃米饭用了11元",
     "output": """date:2023-08-01, amount:11, user_input:前天早上吃米饭用了11元"""},
]

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples=examples,
    embeddings=OpenAIEmbeddings(openai_api_key=openai_api_key),
    vectorstore_cls=FAISS,
    k=3
)

similar_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix="您将从用户那得到一段文字, 解析相关内容并且返回相关的内容",
    suffix="用户输入:{user_input}\n解析结果:",
    input_variables=["user_input"],
)

print(similar_prompt.format(user_input="今天是2023-08-03,今天吃米饭用了10元"))

print(llm(similar_prompt.format(user_input="今天是2023-08-01,前天吃米饭用了3.3元")))

## date:2023-07-30, amount:3.3, user_input:前天吃米饭用了3.3元

```

