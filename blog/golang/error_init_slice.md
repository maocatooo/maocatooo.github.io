---
title: Golang 错误的初始化 Slice, 痛痛痛
date: 2021-07-06
tags: [Golang]
---


### <center>错误的初始化 Slice, 痛痛痛</center>

先上代码

```go
package main

import "fmt"

func main() {
	s := []string{"A", "B", "C"}

	ns1 := newSlice1(s)
	ns2 := newSlice2(s)

	fmt.Printf("value = %+v, %p \n", s, s)     //value = [A2 B C], 0xc00007a330
	fmt.Printf("value = %+v, %p \n", ns1, ns1) //value = [A2], 0xc00007a330
	fmt.Printf("value = %+v, %p \n", ns2, ns2) //value = [A2], 0xc00007a330
}

func newSlice1(s []string) []string {
	ns := s[:0]
	ns = append(ns, "A1")
	return ns
}

func newSlice2(s []string) []string {
	ns := s[:0]
	ns = append(ns, "A2")
	return ns
}
```

重构旧代码的时候, 发现了一些function里使用类似上面
```ns := s[:0]```
来出创建新的Slice, 就是不想导入包, 或少写一些代码 

本以为还有我没学习到的奇技淫巧, 然而发现只要对这种新创建的切片做修改操作, 所有关联使用的地方都会出现修改

**本质这些创建的切片指向的还是同一片内存空间**

因为项目使用只是对切片做一些过滤, 然后返回出去, 这种问题被自然规避掉了

