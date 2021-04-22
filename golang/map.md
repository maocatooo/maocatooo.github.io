# 


map是一堆键值对的未排序集合

map的底层是通过hmap（hashmap）来实现的

hashmap 会存在哈希冲突

解决 hash 冲突办法：

  - 开放寻址法
    - 线性探测法：向后依次探测可以存放的位置，直到找到为止（最坏情况下时间复杂度O(n)）
    - 二次线性探测：当前key存在该地址后偏移量为（1,2,3...）的二次方地址处
    - 双重散列：对hash值使用多组散列函数重新计算位置，直到找到空闲位置为止
  - 链表法: 每个位置对应一个链表，查找key所在的链表，然后在链表顺序查找位置


golang map使用改进的链表法解决冲突


map底层数据结构

```golang

type hmap struct {
	// Note: the format of the hmap is also encoded in cmd/compile/internal/gc/reflect.go.
	// Make sure this stays in sync with the compiler's definition.
    // 当前哈希表元素的数量
	count     int // # live cells == size of map.  Must be first (used by len() builtin)
	flags     uint8
    // 当前 buckets 数量 2^B
	B         uint8  // log_2 of # of buckets (can hold up to loadFactor * 2^B items)
	noverflow uint16 // approximate number of overflow buckets; see incrnoverflow for details
	// hash随机种子
    hash0     uint32 // hash seed
    // buckets 是一个指针，保存bmap位置 bmap是具体存放key-valuue的地方
	buckets    unsafe.Pointer // array of 2^B Buckets. may be nil if count==0.
	oldbuckets unsafe.Pointer // previous bucket array of half the size, non-nil only when growing
	nevacuate  uintptr        // progress counter for evacuation (buckets less than this have been evacuated)

	extra *mapextra // optional fields
}


```
bmap
![bmap](./images/bmap.png)


bmap 创建过多后， golang会将多个bmap合并成一个大的 bmap 以提高性能