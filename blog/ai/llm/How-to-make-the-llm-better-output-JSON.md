---
title: 如何让大模型更好的输出json
date: 2026-05-09 
tags: [OPENAI,LLM]
---

#### 接触大模型

24年做的一个项目，有一个功能，需要把用户上传的图纸识别出商品名，型号，以及材质，还有一些公司信息的敏感内容，

客户提议用当时刚GPT刚出的GPT-4o mini 来做，一套开发下来，上测试，客户发现总是有小情况，识别的内容都是空，安排我去调查
发现就是模型输出和不合规的内容

当时的提示词内容如下
```markdown
You are an image recognition system, you need ...
...
...
You need to output data in JSON structure。
result:
{
  "product_name": "",
  "company_name":"",
  ...
}
``` 
多数情况下，模型都能正常吐内容，少数情况下，返回了
```json
{
  "result":{
      "product_name": "",
      "company_name":"",
      ...
    }
}
```
当时对结果过滤只考虑了 ```json 和 json 合法性的校验，只是没想到有这种情况，只能同时处理了

#### 吐出标准化的json

后来一些项目或多或少都有这种利用大模型输出json的需求了，慢慢结合网上别人的经验和实际使用总结一下

**1. 提示词**  
- 提示词中必须明确用json输出，指定格式，最好有参考示例

**2. openai skd 的 response_format**
- 两种常用模式json_object, json_schema
```markdown
1. json_object
response = client.chat.completions.create(
    ...
    response_format={
        "type": "json_object"
    }
)
2. json_schema / Structured Outputs
response = client.chat.completions.create(
    ...
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "info",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string"
                    },
                    "company_name": {
                        "type": "string"
                    }
                },
                "required": ["product_name", "company_name"],
                "additionalProperties": False
            }
        }
    }
)
```
**3. 校验非标准结果进行多轮对话重新生成** 

在生成完毕后，json字段能对上，但是数据因为模型自身能力/幻觉，json内容牛头不对马嘴   
比如：
- 一个生成题目的智能体,选项ABCD，有时候成为了I,II..
- 还有个单词练习卡片生成需要生成单词字母干扰项，干扰项本应该是单字母形式，结果出现了多个  

在有完善的规则校验下，直接把校验结果返回给AI变成输出，直接进行多轮对话，可以极大的解决这个痛点

```python
MAX_RETRY = 3
user_prompt = "生成一道四选一英语题"
result = llm.generate(user_prompt)
for retry in range(MAX_RETRY):
    validate_result = validator.check(result)
    if validate_result.pass_flag:
        return result
    # 构造纠错Prompt
    repair_prompt = f"""
你生成的结果未通过校验，请仅修正错误部分并重新输出合法JSON。
原始结果：
{result}
校验失败原因：
{validate_result.errors}
规则要求：
1. 选项必须为A/B/C/D
2. 干扰项必须是单个字母
3. JSON结构保持不变
"""
    result = llm.generate(repair_prompt)
raise Exception("重试次数耗尽")
```
