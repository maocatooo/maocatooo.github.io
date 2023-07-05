
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

```
// 从git中删除idea缓存
git rm --cached -r .idea // -r 表示递归

// 生成新的提交
git add .gitignore
git commit -m "(gitignore commit and remove .idea)"

// 提交
git push

```

### 用代理拉github代码

```
// 指定 http 代理 github
git config --global http.https://github.com.proxy http://127.0.0.1:4780

// 拉取代码指定 https 代理 github
git clone https://github.com/xxxxx/xxxxx2.git --config https.proxy=https://127.0.0.1:4780

// 删除代理
git config --global --unset http.https://github.com.proxy
```