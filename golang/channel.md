---
title: Golang Channel
date: 2022-12-30
tags: [Golang]
---
参考 ： 

https://draveness.me/golang/docs/part3-runtime/ch06-concurrency/golang-channel

https://www.bilibili.com/video/BV1kh411n79h

不要通过共享内存的方式进行通信, 而是应该通过通信的方式共享内存

Channel 是 Goroutine 之间的通信方式

```
type hchan struct {
	qcount   uint
	dataqsiz uint
	buf      unsafe.Pointer
	elemsize uint16
	closed   uint32
	elemtype *_type
	sendx    uint
	recvx    uint
	recvq    waitq
	sendq    waitq

	lock mutex
}

type waitq struct {
	first *sudog
	last  *sudog
}

type sudog struct {
	g *g

	next *sudog
	prev *sudog
	elem unsafe.Pointer // data element (may point to stack)

	acquiretime int64
	releasetime int64
	ticket      uint32

	isSelect bool

	success bool

	parent   *sudog // semaRoot binary tree
	waitlink *sudog // g.waiting list or semaRoot
	waittail *sudog // semaRoot
	c        *hchan // channel
}
```

- qcount — Channel 中的元素个数；
- dataqsiz — Channel 中的循环队列的长度；
- buf — Channel 的缓冲区数据指针,是一个环形队列；
- sendx — Channel 的发送操作处理到的位置；
- recvx — Channel 的接收操作处理到的位置；
- elemsize 和 elemtype 分别表示当前 Channel 能够收发的元素类型和大小
- sendq 和 recvq 存储了当前 Channel 由于缓冲区空间不足而阻塞的 Goroutine 列表


### 发送数据

在发送数据的逻辑执行之前会先为当前 Channel 加锁, 防止多个线程并发修改数据。如果 Channel 已经关闭, 那么向该 Channel 发送数据时会报 “send on closed channel” 错误并中止程序

#### 直接发送(无缓冲)

如果目标 Channel 没有被关闭并且已经有处于读等待的 Goroutine, 会从接收队列 recvq 中取出最先陷入等待的 Goroutine 并直接向它发送数据

#### 发送有缓冲

创建的 Channel 包含缓冲区并且 Channel 中的数据没有装满, 计算出下一个可以存储数据的位置, 然后将数据拷贝到环形队列中对应的位置上

#### 阻塞发送

会创建一个等待结构并将其加入 Channel 的 发送队列中, 当前 Goroutine 也会陷入阻塞, 等待其他的协程从 Channel 接收数据


#### 使用 select 关键字可以向 Channel 非阻塞地发送消息
runtime.selectnbsend()

本质上是在 chansend() 上加了判断

###接受消息

- 当存在等待的发送者时, 从阻塞的发送者或者缓冲区中获取数据
- 当缓冲区存在数据时, 从 Channel 的缓冲区中接收数据
- 当缓冲区中不存在数据时, 等待其他 Goroutine 向 Channel 发送数据


#### 直接接收(无缓冲)
将 Channel (sendq)发送队列中 Goroutine 存储的 elem 数据拷贝到目标内存地址中

#### 缓冲区有数据
如果 Channel 的 sendq 发送队列中存在挂起的 Goroutine, 会将 recvx 获取索引所在的数据拷贝到接收变量所在的内存空间上并将 sendq 发送队列中 Goroutine 的数据拷贝到缓冲区
, 然后直接读取 recvx 获取索引对应的数据

#### 缓冲区没有数据

创建一个等待结构并将其加入 Channel 的接受队列中, 当前 Goroutine 陷入阻塞, 等待调度器的唤醒

#### 触发 Goroutine 调度的两个时机：

- 当 Channel 为空时；
- 当缓冲区中不存在数据并且也不存在数据的发送者时