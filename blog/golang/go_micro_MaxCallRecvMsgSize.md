---
title: 微服务框架 go-micro 代理 proxy 接受消息值最大修改
date: 2021-08-06
tags: [Golang, go-micro]
---

### <center> 微服务框架 go-micro 代理 proxy 接受消息值最大修改 </center>

keyword: MaxCallRecvMsgSize

go-micro 框架自带了 proxy 用来代理微服务之间的rpc请求,因为框架内部封装好了 client(本质是服务对服务直接请求) 可以在golang端轻松修改 clientGrpc.MaxRecvMsgSize,clientGrpc.MaxSendMsgSize 来设置请求数据

go-micro 框架默认服务间最大响应值是4M.

```
# 启动 proxy
set MICRO_REGISTRY=etcd
set MICRO_REGISTRY_ADDRESS=127.0.0.1:2379
micro proxy
```

然而在 micro proxy 中这两个参数是失效的,导致公司C++客户端进行rpc调用的时候不能请求一些大型的数据内容,追了一下源码,发现grpc官方已经把4M固定死,但是还是留了口子让我们通过CallOption改动对应的值

前置条件:

所有的 service 必须修改 DefaultMaxMsgSize

```

import (
    ...
    serverGrpc "github.com/micro/go-micro/v2/server/grpc"
    
)

const maxMsgSize int = 8 * 1024 * 1024

func init()  {
    serverGrpc.DefaultMaxMsgSize = maxMsgSize
}

```

构建proxy

改动点有两个

1. init 方法中必须要把 micro server 的 DefaultMaxMsgSize改掉

2. 然后就是 Client.Init 去初始化 CallOption

```
// proxy.go

package main

import (
    "github.com/micro/go-micro/v2"
    "github.com/micro/go-micro/v2/client"
    clientGrpc "github.com/micro/go-micro/v2/client/grpc"
    serverGrpc "github.com/micro/go-micro/v2/server/grpc"
    "github.com/micro/micro/v2/cmd"
    "google.golang.org/grpc"
)

const maxMsgSize int = 8 * 1024 * 1024

func init()  {
    serverGrpc.DefaultMaxMsgSize = maxMsgSize
}

func main()  {

    cmd.Init(func(options *micro.Options) {
        err := options.Client.Init(func(options *client.Options) {
            clientGrpc.CallOptions(grpc.MaxCallRecvMsgSize(maxMsgSize))(&options.CallOptions)
        })
        if err != nil {
            panic(err)
        }
    })
}


```
```
# 启动 proxy
set MICRO_REGISTRY=etcd
set MICRO_REGISTRY_ADDRESS=127.0.0.1:2379
go run proxy.go proxy
```
