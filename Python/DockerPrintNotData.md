---
title: Python print() 在 Docker 不输出
date: 2024-10-30
tags: [Python]
---

print 输出有缓冲

解决办法
1. Dockerfile
    ```shell
    ENV PYTHONUNBUFFERED=1
    ```
2. docker run 
    ```shell
    docker run -e PYTHONUNBUFFERED=1
    ```
3. print中的flush=True
    ```shell
    print("start", flush=True)
    ```
   
一个使用python起docker守护进程的命令
```shell
# python3 -m http.server 8000

 docker run --name test-run -it -d amazonlinux:2023 python3 -m http.server 8000
```