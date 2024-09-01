
---
title: coding手册
date: 2023-01-01 12:00:00
tags: [coding手册,参考资料]
---


### 时间处理

```js
// 获取毫秒时间戳
new Date().getTime() 
// 自定义格式
moment().format('YYYY-MM-DD HH:mm:ss');
moment(new Date()).format('YYYY-MM-DD HH:mm:ss');
```

```go
// 获取毫秒时间戳
time.Now().UnixMilli()
// 自定义格式
time.Now().Format("2006-01-02 15:04:05")
```

```python
// 获取毫秒时间戳
time.time()
// 自定义格式
datetime.now().strftime('%Y-%m-%d %H:%M:%S')
```
