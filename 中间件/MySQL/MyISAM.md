### InnoDB 和 MyISAM 的锁

MyISAM 只支持表锁

MyISAM 在 SELECT 的时候会自动给表加上读锁, 在执行 UPDATE, DELETE, INSERT 的时候会自动给涉及的表加上写锁, 在操作完成是会释放锁。


#### 当前会话(线程)对表加上读锁, 必须解锁后才能操作其他表, 对其他会话无影响
```SQL

对 MyISAM 显示加锁

# 读锁
lock table table_bane read;

# 写锁
lock table table_name write;

# 解锁
unlock tables;

```

读锁会阻塞写操作, 但是不会阻塞读操作, 写锁, 读写操作都会阻塞

查看锁的争用情况

```sql
show open tables;
```

In_use： 表的使用次数

Name_locked: 表名锁定,  用于取消表获取对表进行重命名等操作

```sql
show status like "Tabke_lock%";
```

Table_locks_immediate : 指的是能够立即获得表锁的次数, 每立即获得锁, 便+1

Table_locks_waited ：指的是不能够立即获得表锁的次数, 每等待一次, 便+1,  值越高说明争抢情况严重


MyISAM 适合大量读操作