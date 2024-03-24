---
title: 避坑之 grpc metadata 不能存入非 ASCll 字符
date: 2023-07-06 
tags: [Golang, gRPC]
---

### grpc metadata 不能存入非 ASCll 字符

```
rpc error: code = Internal desc = header key "user_name" contains value with non-printable ASCll characters
```

项目中进行 rpc 调用的时候出现这个问题,问题很容易追踪, 就是在
metadata.AppendToOutgoingContext 里user_name对应的value存入中文

在 grpc 源码中就能找到对应的限制, 如果非要进行中文传输,可以添加后缀`-bin`(例如:`user_name-bin`), 表示对应的数据通过二进制数据进行编码解码传输

```go
google.golang.org/grpc/internal/metadata/metadata.go:90
// hasNotPrintable return true if msg contains any characters which are not in %x20-%x7E
func hasNotPrintable(msg string) bool {
	// for i that saving a conversion if not using for range
	for i := 0; i < len(msg); i++ {
		if msg[i] < 0x20 || msg[i] > 0x7E {
			return true
		}
	}
	return false
}
```
