---
title: git手册
date: 2020-03-04
tags: [git手册]
---

### 本地项目和远程关联
```shell
git init

git remote add origin https://xxx/xx.git

git pull --rebase origin master
```

### 添加多个仓库并且提交,拉取代码
```shell
// 添加一个 remote=origin的仓库地址
git remote add origin https://github.com/xx.git

// 添加一个 remote=gitee的仓库地址
git remote add gitee https://gitee.com/xx.git

// 拉取remote=gitee的代码
git pull gitee master

// 提交remote=gitee的代码
git push gitee master
```

### .gitignore忘了添加忽略的文件导致提交了不需要的文件
**.gitignore添加忽略的文件夹**
```shell
// 从git中删除idea缓存
git rm --cached -r .idea // -r 表示递归

// 生成新的提交
git add .gitignore
git commit -m "(gitignore commit and remove .idea)"

// 提交
git push

```

### 用代理拉github代码
```shell
// 指定 http 代理 github
git config --global http.https://github.com.proxy http://127.0.0.1:4780

// 拉取代码指定 https 代理 github
git clone https://github.com/xxxxx/xxxxx2.git --config http.proxy=http://127.0.0.1:4780

// 删除代理
git config --global --unset http.https://github.com.proxy
```

### 保存登录状态
```shell
git config --global credential.helper 'store'
```

### 保存登录状态
```shell
git config --global credential.helper 'store'
```

### 使用强制重置回滚最新的提交
```shell
git reset --hard HEAD^
```

### git 重做
```shell
git revert HEAD
```

### 忽略提交文件
```shell
git update-index --assume-unchanged etc/config_test.yaml

// 取消
git update-index --no-assume-unchanged etc/config_test.yaml
```

### git 忽略https证书
```shell
set GIT_SSL_NO_VERIFY=true
```