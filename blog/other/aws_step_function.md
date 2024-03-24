---
title: AWS之Step Functions
date: 2024-03-25
tags: [aws,Step Functions]
---

### Step Functions
官方文档:https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html

公司中的项目需要用到延时任务去处理业务上的问题,AWS自带的SQS消息延时队列最大的延时消息是15分钟,完全不能满足我们可以自定义或固定超过15分钟去处理延时任务

因此,领导安排我调研AWS Step Functions看看能不能解决这些问题

Step Functions 基于状态机和任务。在 Step Functions 中，工作流被称为状态机，它是一系列事件驱动的步骤。
工作流程中的每个步骤都称为状态。状态代表其他AWS服务（例如AWS Lambda）执行的工作单元。任务状态可以调用任何AWS服务或API任务

Step Functions 也提供了等待状态传入自定义时间来控制任务处理, 用来做延时任务确实符合我们的业务场景

(虽然最后没有选择使用此方案做延时任务, 因为最大的活动数量上限是10000 不能满足我们的业务量对应的需求)

#### 使用 AWS Step Functions 做延时任务

流程步骤

1. 创建lambda函数
2. 创建状态机添加延时任务并且绑定lambda函数
3. 执行状态机


配置本地开发环境

前置条件 安装 aws-cli, sam-cli

lambda 函数
1. 创建lambda函数
   sam init
2. 编译打包
   sam build
3. 本地运行
   sam local start-lambda --host 0.0.0.0

创建状态机环境
docker run --name stepfunctions -p 8083:8083 --env-file env.txt amazon/aws-stepfunctions-local

环境变量env.txt
```
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=012345678901
AWS_SECRET_ACCESS_KEY=012345678901
LAMBDA_ENDPOINT=http://10.0.8.246:3001  # 本地运行的lambda函数地址
```


创建状态机
```python
import json
import os

states = {
    "Comment": "example",
    "StartAt": "wait_until",
    "States": {
        "wait_until" : {
            "Type": "Wait", # 等待状态
            "SecondsPath": "$.expirydate", # 从输入中获取延时时间
            "Next": "LambdaState"
        },
        "LambdaState": {
            "Type": "Task", # 任务状态
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload", # 从lambda函数的返回值中获取输出
            "Parameters": {
                "Payload.$": "$", # 将输入传递给lambda函数
                "FunctionName": "arn:aws:lambda:us-east-1:function:HelloWorldFunction:$LATEST" # lambda函数的arn
            },
            "Next": "NextState"
        },
        "NextState": {
            "Type": "Pass",
            "End": True
        }
    }
}

states_str = (json.dumps(json.dumps(states)))

cmd = "aws stepfunctions --endpoint http://localhost:8083 create-state-machine --definition " + states_str + " --name test --role-arn arn:aws:iam::123456789012:role/DummyRole"

os.system(cmd)
```

删除状态机
aws stepfunctions --endpoint-url http://localhost:8083 start-execution --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld --input "{\"a\":1}"

golang执行状态机方法并且传递参数
```go
package main

import (
	"fmt"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/sfn"
	"log"
)

func main() {
	// 创建 AWS 会话
	sess, err := session.NewSession(&aws.Config{
		Region:   aws.String("us-east-1"),             // 替换为 AWS 区域
		Endpoint: aws.String("http://localhost:8083"), // 替换为 Step Functions 本地端点
	})
	if err != nil {
		log.Fatal(err)
	}

	// 创建 Step Functions 客户端
	sfnClient := sfn.New(sess)

	// 定义输入参数
	input := `{"expirydate":11, "a":1233333}`

	// 指定状态机的 ARN
	stateMachineARN := "arn:aws:states:us-east-1:123456789012:stateMachine:test"

	// 调用状态机
	result, err := sfnClient.StartExecution(&sfn.StartExecutionInput{
		Input:           &input,
		StateMachineArn: &stateMachineARN,
	})
	if err != nil {
		log.Fatal(err)
	}

	// 打印执行的 ARN
	fmt.Println("Execution ARN:", *result.ExecutionArn)
}
```


