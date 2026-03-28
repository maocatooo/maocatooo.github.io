---
title: graphrag 1.2 增量训练文件  
date: 2026-03-28 20:43:12
tags: [graphrag]
---

## 注意
**settings.yaml 不动，update_index_storage 放开会导致 index 时候出错，所以不能动**

> 建议把训练目录和查询目录分开，保证在新训练时不影响旧数据，避免一些其他影响

---

## 操作步骤

### 1. 复制原有目录文件夹到训练文件夹
```bash
cp /data/gr_data_search/xxxx/xxx /data/gr_data/xxxx/xxx
````

---

### 2. 增量训练

**注意：**
`settings.yaml` 中的 `title` 字段不能和之前已训练过的数据重复，否则会跳过数据

```bash
python3.12 training.py update --root /data/gr_data/xxxx/xxx
```

训练完成后会生成新目录 `update_output`：

* `update_output`：原始内容 + 增量内容
* `update_output/delta`：仅增量内容
* `lancedb` 目录：`output/lancedb` 已自动更新，无需操作

---

### 3. 复制覆盖结构化数据

```bash
cp update_output/*.parquet output/

# 删除临时目录
rm -r update_output
```

---

### 4. 新上传

---

### 5. 备注

* `index` 和 `update` 都会使用缓存数据 `cache`，建议在重新训练或 update 时复用，可以提速并节省成本

* 删除文件只能通过重新 `index` 重建：

```bash
rm -r output
```

> update 只负责增量添加，不支持删除 

