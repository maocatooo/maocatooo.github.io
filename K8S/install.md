---
title: 安装 K8s
date: 2022-01-01
tags: [K8S]
---


### kubeadm 安装 K8s



### 关闭防火墙：
```
systemctl stop firewalld

systemctl disable firewall

```
### 关闭 selinux：
```
sed -i 's/enforcing/disabled/' /etc/selinux/config # 永久
setenforce 0 # 临时
```

### 关闭 swap：
```
swapoff -a # 临时
sed -ri 's/.*swap.*/#&/' /etc/fstab # 永久
```

### 将桥接的 IPv4 流量传递到 iptables 的链：
```
cat > /etc/sysctl.d/k8s.conf << EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sysctl --system # 生效
```
### 设置hostname

```
hostnamectl set-hostname node1
```

### 添加host
```
cat >> /etc/hosts << EOF
192.168.223.132 node1
192.168.223.133 node2
192.168.223.134 node3
EOF
```
### 安装docker

```
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
```

### 安装并启动 docker
```
yum install -y docker-ce-19.03.8 docker-ce-cli-19.03.8 containerd.io
systemctl enable docker
dsystemctl start docker

```
#### 阿里云docker镜像加速
```
mkdir -p /etc/docker
tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://3p9gqnrv.mirror.aliyuncs.com"]
}
EOF
systemctl daemon-reload
systemctl restart docker
```

### 安装k8s、kubelet、kubeadm、kubectl（所有节点）
```
# 配置K8S的yum源
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
       http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF

# 卸载旧版本
yum remove -y kubelet kubeadm kubectl

# 安装kubelet、kubeadm、kubectl
yum install -y kubelet-1.17.3 kubeadm-1.17.3 kubectl-1.17.3

#开机启动和重启kubelet
systemctl enable kubelet && systemctl start kubelet
##注意, 如果此时查看kubelet的状态, 他会无限重启, 等待接收集群命令, 和初始化。这个是正常的。

kubeadm 初始化master 
 kubeadm init \
--apiserver-advertise-address=192.168.223.132 \
--image-repository registry.aliyuncs.com/google_containers \
--kubernetes-version v1.17.3 \
--service-cidr=10.96.0.0/12 \
--pod-network-cidr=10.244.0.0/16
```

```
# worker加入集群

#1、使用刚才master打印的令牌命令加入
kubeadm join 172.26.248.150:6443 --token ktnvuj.tgldo613ejg5a3x4 \
    --discovery-token-ca-cert-hash sha256:f66c496cf7eb8aa06e1a7cdb9b6be5b013c613cdcf5d1bbd88a6ea19a2b454ec

#2、如果超过2小时忘记了令牌, 可以这样做
kubeadm token create --print-join-command #打印新令牌
kubeadm token create --ttl 0 --print-join-command #创建个永不过期的令牌
```