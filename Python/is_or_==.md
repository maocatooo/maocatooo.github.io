is 和 == 的区别

---

都是对象的比较
is 比较的是内存地址

```python
>>>1 is 1
True
>>>[1, 2] is [1, 2]
False
# 因为 id([1, 2]) 都不同
```

== 是两个对象的__eq__方法返回的值进行比较

因此可以重载__eq__来实现不同对象的比较

```python

class NewInt(int):
    def __eq__(self, other):
        return str(self) == str(other)


ni = NewInt(1)
print(ni == "1") # True

```


