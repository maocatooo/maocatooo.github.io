---
title: 服务器时间导致服务崩溃
date: 2025-08-11 18:15:42
tags: [GPT5,OPENAI,LLM]
---


### gpt-5:  
https://platform.openai.com/docs/guides/latest-model?reasoning-effort-mode=responses#prompting-guidance
https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools#4-minimal-reasoning

#### 缓存(旧概念):  
https://platform.openai.com/docs/guides/prompt-caching

OpenAI 会将 API 请求路由到最近处理过相同提示的服务器上，从而以比从头开始处理更低的成本和更快的速度完成请求。这种方法可将延迟降低高达 80%，成本降低高达 75%  


当提示词达到或超过 1024 个 token 时，缓存将自动启用。当发起 API 请求时，将发生以下步骤：  
- 缓存路由：  
  - 请求会根据提示词初始前缀的哈希值被路由到特定机器。哈希通常使用前 256 个 token，但具体长度可能因模型而异。  
  - 如果提供了prompt_cache_key参数，它将与前缀哈希值结合使用，从而允许影响路由并提高缓存命中率。当多个请求共享较长的公共前缀时，这一点尤为有益。  
  - 如果针对相同前缀和 prompt_cache_key 组合的请求超过一定频率（约每分钟 15 次），部分请求可能会溢出并被路由到其他机器，从而降低缓存效率。  
- 缓存查找：系统会检查所选机器上的缓存中是否存在提示词的初始部分（前缀）。  
- 缓存命中：如果找到匹配的前缀，系统将使用缓存结果。这将显著降低延迟并减少成本。  
- 缓存未命中：如果未找到匹配的前缀，系统将处理完整提示词，并在该机器上缓存其前缀，供后续请求使用。  
已缓存的前缀通常在连续 5 到 10 分钟无活动后失效。但在非高峰时段，缓存可能最长保留一小时。  


#### 记忆(旧概念)：
https://help.openai.com/en/collections/8471548-memory
https://www.tomsguide.com/ai/chatgpt-5-features-heres-the-5-upgrades-i-would-try-first

#### 性格:
https://help.openai.com/en/articles/11899719-customizing-your-chatgpt-personality

**记忆和性格都是在GPT自家的应用中使用的**


### 模型
| 模型         |  特点 | 参数                                                                                                                     |   |
|------------|---|------------------------------------------------------------------------------------------------------------------------|---|
| GPT-5      |  在各个领域进行编码、推理和代理任务的旗舰模型 |                     400,000 context window <br />128,000 max output tokens  <br /> May 31, 2024 knowledge cutoff <br /> Reasoning token support                                                                                                    |   |
| GPT-5 mini |  一个更快、更具成本效益的版本。非常适合定义明确的任务和精确的提示。 | 400,000 context window <br />128,000 max output tokens  <br /> May 31, 2024 knowledge cutoff <br /> Reasoning token support |   |
| GPT-5 nano |  最快、最经济的 GPT-5 版本。非常适合摘要和分类任务 | 400,000 context window <br />128,000 max output tokens  <br /> May 31, 2024 knowledge cutoff <br /> Reasoning token support |   |


### 价格对比

| 模型         | 输入    | 缓存    | 输出     |   
|------------|-------|-------|--------|
| GPT-5      | $1.25 | $0.13 | $10.00 | 
| GPT-5 mini | $0.25 | $0.03 | $2.00  |  
| GPT-5 nano | $0.05 | $0.01 | $0.40  |  
| GPT-4o     | $2.50 | $1.25 | $10.00 | 
| GPT-4.1    | $2.00 | $0.50 | $8.00  | 
| o3-mini    | $1.10 | $0.55 | $4.40  | 



## 接口调用新参数

### 1.  `verbosity` 参数
```python

client = OpenAI()
for verbosity in ["low", "medium", "high"]:
    response = client.responses.create(
        model="gpt-5-mini",
        input="写一首关于一个男孩和他的第一只宠物狗的诗",
        text={"verbosity": verbosity}
    )
```

可以在不改变底层提示词的情况下，稳定地同时调整模型输出的长度和深度，并且保持正确性和推理质量。  

low: 简洁的用户体验，文字最少  
medium(默认值): 细节与简洁平衡   
high: 内容详尽，适合审查、教学。  

测试使用token消耗比重：   
low:medium:high ---  **424:530:1072**  


### 2. 自由形式函数调用 Freeform Function Calling


#### 示例

```python

client = OpenAI()

response = client.responses.create(
    model="gpt-5-mini",
    input="请使用code_exec工具计算 100 以内的质数之和。",
    text={"format": {"type": "text"}},
    tools=[
        {
            "type": "custom",
            "name": "code_exec",
            "description": "Executes arbitrary python code",
        }
    ]
)
```

GPT-5 中的自由形式工具调用允许将原始文本载荷——例如 Python 脚本、SQL 查询或配置文件——直接发送到自定义工具，而无需使用 JSON 封装  
(本质就是将一段文本交给工具处理)

#### 对比function 工具(gpt会返回json格式文本)
```python
tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"],
        "additionalProperties": False
    },
    "strict": True
}]
```

### 3. 上下文无关语法 Context‑Free Grammar (CFG)

在custom tools中，可以使用上下文无关语法 CFG 限制输出， 确保自定义工具的输入符合预期。

"syntax": "lark"
"syntax": "regex"

#### 示例
```python

client = OpenAI()

timestamp_grammar_definition = r"^\d{1}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) (?:[01]\d|2[0-3]):[0-5]\d$"

timestamp_prompt = (
    "Call the timestamp_grammar to save a timestamp for August 7th 2025 at 10AM."
)

response_mssql = client.responses.create(
    model="gpt-5",
    input=timestamp_prompt,
    text={"format": {"type": "text"}},
    tools=[
        {
            "type": "custom",
            "name": "timestamp_grammar",
            "description": "Saves a timestamp in date + time in 24-hr format.",
            "format": {
                "type": "grammar",
                "syntax": "regex",
                "definition": timestamp_grammar_definition
            }
        },
    ],
    parallel_tool_calls=False
)
```

### 4.  Minimal Reasoning
Minimal reasoning 通过使用极少或不使用推理 token 来运行 GPT-5，以最大限度地降低延迟并加快首字输出时间。适用于无需解释的确定性、轻量级任务（如信息提取、格式化、简短重写、简单分类）。若不指定 effort 参数，默认为 medium；当您优先考虑速度而非深入推理时，请显式设置为 minimal。

```python
from openai import OpenAI

client = OpenAI()

prompt = "Classify sentiment of the review as positive|neutral|negative. Return one word only." 


response = client.responses.create(
    model="gpt-5",
    input= [{ 'role': 'developer', 'content': prompt }, 
            { 'role': 'user', 'content': 'The food that the restaurant was great! I recommend it to everyone.' }],
    reasoning = {
        "effort": "minimal"
    },
)
```