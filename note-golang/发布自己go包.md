
#### <center>发布自己 golang package</center>


1. 代码提交到自己的github项目库 并且上tag
    
   例如: `github.com/maocatooo/thin`
   ```
   git tag v0.0.1
   git push origin v0.0.1
   ```

2. 告诉golang 代理服务器更新其索引

   1. 访问 https://pkg.go.dev/github.com/maocatooo/thin 提交自己项目链接
   
   2.  
       ```
       set GOPROXY=proxy.golang.org
       go list -m github.com/maocatooo/thin@v0.0.1
       ```
       然而因为代理问题大概率是会超时的,
       
       解决办法:在浏览器打开 https://proxy.golang.org/github.com/maocatooo/thin/@v/v0.0.1.info"
       
3. 等待一段时间就好