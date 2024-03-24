---
title: 在golang中使用 NACOS 管理项目的配置文件
date: 2022-02-26 
tags: [Golang, NACOS]
---

### <center> 在golang中使用 NACOS 管理项目的配置文件 </center>

* [安装Nacos](../../中间件/Nacos/install.md)

nacos go

```shell
go get github.com/nacos-group/nacos-sdk-go/v2@v2.2.1
```

```go
package main

import (
	"fmt"
	"github.com/nacos-group/nacos-sdk-go/v2/clients"
	"github.com/nacos-group/nacos-sdk-go/v2/common/constant"
	"github.com/nacos-group/nacos-sdk-go/v2/vo"
)

// NACOS 2.2.2
func main() {

	//create clientConfig
	clientConfig := constant.ClientConfig{
		NamespaceId:         "", //we can create multiple clients with different namespaceId to support multiple namespace.When namespace is public, fill in the blank string here.
		TimeoutMs:           500,
		NotLoadCacheAtStart: true,
		LogDir:              ".",
		CacheDir:            ".",
		LogLevel:            "debug",
		Username:            "nacos",
		Password:            "nacos",
	}

	// At least one ServerConfig
	serverConfigs := []constant.ServerConfig{
		{
			IpAddr:      "172.25.89.138",
			ContextPath: "/nacos",
			Port:        8848,
			Scheme:      "http",
		},
		//{
		//	IpAddr:      "console2.nacos.io",
		//	ContextPath: "/nacos",
		//	Port:        80,
		//	Scheme:      "http",
		//},
	}

	configClient, err := clients.NewConfigClient(
		vo.NacosClientParam{
			ClientConfig:  &clientConfig,
			ServerConfigs: serverConfigs,
		},
	)
	if err != nil {
		panic(err)
	}
	// 添加修改配置文件
	ok, err := configClient.PublishConfig(vo.ConfigParam{
		DataId:  "config_pre.yaml",
		Group:   "DEFAULT_GROUP",
		Content: `ddd:123`,
	})
	if err != nil {
		panic(err)
	}
	fmt.Println(ok)
	// 查找配置文件
	data, err := configClient.GetConfig(vo.ConfigParam{
		DataId: "config_pre.yaml",
		Group:  "DEFAULT_GROUP",
	})
	if err != nil {
		panic(err)
	}
	fmt.Println(data)
	// 监听配置文件变动
	err = configClient.ListenConfig(vo.ConfigParam{
		DataId: "config_pre.yaml",
		Group:  "DEFAULT_GROUP",
		OnChange: func(namespace, group, dataId, data string) {
			fmt.Println("group:" + group + ", dataId:" + dataId + ", data:" + data)
		},
	})
	if err != nil {
		panic(err)
	}
	select {}
}


```