### <center>记一次 Golang 定时器 cpu 使用率过高的问题</center>

早上打开电脑摸鱼的时候发现公司的测试环境的一个微服务CPU单核占用率到了99%,因为是核心服务,一直以为是处理业务逻辑的原因, 下午的时候就飙到了199%,而且很稳定的维持中,发现不对劲,去其他环境一看,果然这个服务的CPU占用率都不正常, 很可惜没有对这个服务开启pprof,找不到具体原因, 看看代码, 很顺利找到原因

看到代码时立马想到了当年看过群主的这篇[blog]( https://xiaorui.cc/archives/5117)

原因还是锁抢占的问题

demo 如下

```golang

func run() {
  go func() {
     for i := 0; i <= 100; i++ {
       go func() {
         timeOut := time.NewTimer(time.Second * 120)
         t := time.NewTicker(time.Millisecond * 50)
         for {
           select {
           case <-t.C:
           	   ...check
           case <-timeOut.C:
             break
           }
         }
       }()
     }
   }()
 }

```

稍微加大协程运行等待一段时间,cpu占用率果然上来了

![cpu占用率](../images/微信图片_20221228215317.jpg)

后来重构了这块代码,不在使用time.NewTicker才解决这个问题



