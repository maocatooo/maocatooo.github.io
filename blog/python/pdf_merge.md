---
title: 使用python把多个pdf合并为一个pdf文件
date: 2025-01-21
tags: [Python,PDF]
---


##### 安装PyPDF2
```shell
pip install PyPDF2
```

##### 合并pdf文件
```python
from PyPDF2 import PdfMerger


def merge_pdfs(pdf_list, output_file):
    merger = PdfMerger()
    try:
        for pdf in pdf_list:
            merger.append(pdf)
        merger.write(output_file)
        print(f"PDF 文件已成功合并并保存为 {output_file}")
    except Exception as e:
        print(f"合并过程中出现错误: {e}")
    finally:
        merger.close()


pdf_files = ["a.pdf"] * 10  
output_pdf = "merged_output.pdf"
merge_pdfs(pdf_files, output_pdf)

```