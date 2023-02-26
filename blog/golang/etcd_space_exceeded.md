### <center> etcd 超出空间导致服务注册不成功</center>


`keyword：mvcc: database space exceeded`

go-micro 使用etcd作为注册中心, 公司当前处于的是业务开发状态, 发布订阅功能也是直接基于go-micro 使用etcd来做消息转存的,导致消息发布有大量消息没有及时处理, 堆积下来, 然后新服务不能写入注册信息到etcd中

上网搜索了一下,官方文档已经写的很清楚了 https://etcd.io/docs/v3.4/faq/#deployment ,大意是, 为了防止性能下降或无意中使键值存储过载,etcd强制将可配置的存储大小配额默认设置为2GB

解决办法,执行下面命令清空磁盘,然后等待一段时间就行了

```shell
# 查看警告信息
$ etcdctl --endpoints=http://127.0.0.1:2379 alarm list
  memberID:8630161756594109333 alarm:NOSPACE
# 获取当前版本
$ rev=$(etcdctl --endpoints=http://127.0.0.1:2379 endpoint status --write-out="json" | egrep -o '"revision":[0-9]*' | egrep -o '[0-9].*')
# 压缩旧版本
$ etcdctl --endpoints=http://127.0.0.1:2379 compact $rev 
# 清理磁盘碎片
$ etcdctl --endpoints=http://127.0.0.1:2379 defrag
# 最后验证空间是否释放
$ etcdctl endpoint status # 惊人 G变成了M
# 最后清除警告
$ etcdctl --endpoints=http://127.0.0.1:2379 alarm disarm

```
