
#### docker 安装 NACOS

NACOS 当前版本  2.2.2
```

docker run -d -p 8848:8848 -p 9848:9848 -e MODE=standalone \
-e PREFER_HOST_MODE=hostname \
-e NACOS_AUTH_ENABLE=true \
-e NACOS_AUTH_IDENTITY_KEY=test \
-e NACOS_AUTH_IDENTITY_VALUE=test \
-e NACOS_AUTH_TOKEN=MTIzNDU2Nzg5MTIzNDU2Nzg5MTIzNDU2Nzg5MTIzNDU2Nzg5 \
-v $HOME/nacos/logs:/home/nacos/logs \
--restart always --name nacos nacos/nacos-server
```

```
访问地址 http://127.0.0.1:8848/nacos
默认账号密码 
nacos
nacos
```

```
挂载自定义config,需要

-v $HOME/nacos/config/application.properties:/home/nacos/conf/application.properties \

```