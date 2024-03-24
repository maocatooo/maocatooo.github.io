---
title: 用反射闭包了一下 Gin 的 HandlerFunc, 我终于可以开开心心的写单元测试了
date: 2023-03-06
tags: [Golang, Gin]
---

### <center> 用反射闭包了一下 Gin 的 HandlerFunc, 我终于可以开开心心的写单元测试了 </center>

上家公司是用 go-micro 写 rpc, 现在跑过来写 gin, 写单元测试构造用例可太麻烦了

用反射封装了一下，我又回到当初写微服务的快乐了

没有破坏路由也没有破坏中间件，就加了 req 和 resp 的反射封装

基佬链接: https://github.com/maocatooo/thin/tree/main/gin_handler

求个 star

废话多说，上个例子

```
go get -u github.com/maocatooo/thin
```


```go
package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/maocatooo/thin/gin_handler"
)

type Req struct {
	Name string `json:"name"`
}

type Query struct {
	Name string `form:"name"`
}

type Resp struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

/*
GET http://127.0.0.1:8080/ping?name=123
*/
func Ping(ctx *gin.Context, req *Query, rsp *Resp) error {
	fmt.Printf("Ping req: %+v \n", *req)
	if req.Name == "123" {
		return fmt.Errorf("err 123")
	}
	rsp.Code = 200
	rsp.Message = req.Name
	return nil
}

type A struct {
	a string
}

/*
POST http://127.0.0.1:8080/pong
{
	"name":"456"
}
*/
func (a A) Pong(ctx *gin.Context, req *Req, rsp *Resp) error {
	fmt.Printf("Pong req: %+v \n", *req)
	if req.Name == "123" {
		return fmt.Errorf("123")
	}
	rsp.Code = 200
	rsp.Message = req.Name
	return nil
}

func main() {
	r := gin.Default()
	r.GET("/ping", gin_handler.Query(Ping))
	r.POST("/pong", gin_handler.JSON(A{a: "a123"}.Pong))
	_ = r.Run()
}

```
