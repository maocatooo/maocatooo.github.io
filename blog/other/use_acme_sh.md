---
title: 由 certbot 切换到 acme.sh, 使用acme.sh进行SSL证书申请
tags: [ acme.sh, SSL, HTTPS ]
date: 2025-12-20
---


certbot 用来申请SSL证书也是极好的，够用的，acme.sh 很多人推荐，我自己也star了好多年，一直拖着想尝试，最近试了下，用起来还是不错，

github地址：https://github.com/acmesh-official/acme.sh


### nginx配置
```nginx
server { 
    listen 80; 
    server_name api.xxxxx.cn; 
    location / { 
    proxy_pass http://127.0.0.1:5015; 
}
```


### 申请证书

```shell
acme.sh --issue --nginx -d  api.xxxx.cn --force
```
acme.sh 脚本默认 CA 服务器是 [ZeroSSL](https://acme.zerossl.com/v2/DV90), 国内访问经常抽风, 多等等也许会好   
也可以切换到 [Let's Encrypt](https://letsencrypt.org/)]
```shell
acme.sh --set-default-ca --server letsencrypt
```


### 安装证书

```  shell
mkdir -p /etc/nginx/ssl/api.xxxx.cn

acme.sh --install-cert -d api.xxxx.cn \
--key-file       /etc/nginx/ssl/api.xxxx.cn/key.pem \
--fullchain-file /etc/nginx/ssl/api.xxxx.cn/fullchain.pem \
--reloadcmd     "nginx -s reload"
```


### 配置nginx

配置完毕，重启nginx，然后没啥事儿了

```shell

server {
    listen 80;
    server_name api.xxxx.cn;
    #ACME_NGINX_START
    location ~ "^/\.well-known/acme-challenge/([-_a-zA-Z0-9]+)$" {
      default_type text/plain;
      return 200 "$1.2THoePkTTzFjYUI_9CZXr7mt5Li4ESUg3DtzLyuQsm0";
    }
    #NGINX_START

    return 301 https://$host$request_uri;
}

# HTTPS
server {
    listen 443 ssl ;
    server_name api.xxxx.cn;

    ssl_certificate     /etc/nginx/ssl/api.xxxx.cn/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/api.xxxx.cn/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:5015;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        # WebSocket（安全保留）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```