---
title: Kubernetes 容器编排实战入门
date: 2026-05-18 17:00:00
tags:
  - Kubernetes
  - 容器编排
categories:
  - 云原生
---

## 引言

Kubernetes（简称 K8s）作为目前最流行的容器编排平台，已经成为云原生时代的基石技术。无论是微服务架构的落地，还是 DevOps 流程的自动化，K8s 都扮演着不可或缺的角色。本文将系统梳理 K8s 的核心概念，并结合实战示例帮助读者快速上手。

<!-- more -->

## 一、Kubernetes 是什么

Kubernetes 是 Google 开源的容器集群管理系统，基于其内部运行多年的 Borg 系统经验构建。它提供了以下核心能力：

- **容器编排**：自动化部署、扩展和管理容器化应用
- **服务发现与负载均衡**：自动分配容器 IP 和 DNS，实现流量分发
- **存储编排**：支持多种存储后端（本地、云存储、网络存储等）
- **自动回滚与滚动更新**：零停机发布，失败自动回滚
- **自我修复**：容器故障自动重启、替换、重新调度

## 二、核心架构

### 2.1 控制平面（Control Plane）

控制平面负责集群的整体决策和事件响应，核心组件包括：

| 组件 | 职责 |
|------|------|
| **kube-apiserver** | 暴露 Kubernetes API，是集群的前端入口 |
| **etcd** | 分布式键值存储，保存集群所有数据 |
| **kube-scheduler** | 监听新 Pod，选择合适的 Node 进行调度 |
| **kube-controller-manager** | 运行控制器进程（节点、副本、端点等） |
| **cloud-controller-manager** | 对接云厂商 API（如负载均衡、存储卷） |

### 2.2 工作节点（Worker Node）

每个工作节点上运行以下组件：

- **kubelet**：接收 API Server 指令，管理 Pod 生命周期
- **kube-proxy**：维护节点网络规则，实现 Service 负载均衡
- **容器运行时**：如 containerd、CRI-O，负责拉取镜像和运行容器

```
┌─────────────────────────────────────────────────────────┐
│                    Control Plane                         │
│  ┌──────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ kube-apiserver│  │ etcd     │  │ kube-scheduler   │  │
│  └──────────────┘  └──────────┘  └──────────────────┘  │
│  ┌──────────────────────┐  ┌────────────────────────┐  │
│  │ kube-controller-mgr  │  │ cloud-controller-mgr   │  │
│  └──────────────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Worker    │  │  Worker    │  │  Worker    │
    │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │
    │ │ kubelet│ │  │ │ kubelet│ │  │ │ kubelet│ │
    │ ├────────┤ │  │ ├────────┤ │  │ ├────────┤ │
    │ │kube-proxy│ │  │ │kube-proxy│ │  │ │kube-proxy│ │
    │ ├────────┤ │  │ ├────────┤ │  │ ├────────┤ │
    │ │containerd│ │  │ │containerd│ │  │ │containerd│ │
    │ └────────┘ │  │ └────────┘ │  │ └────────┘ │
    └────────────┘  └────────────┘  └────────────┘
```

## 三、核心资源对象

### 3.1 Pod

Pod 是 K8s 中最小的可部署单元，一个 Pod 可以包含一个或多个容器，这些容器共享网络和存储。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
    - name: nginx
      image: nginx:1.25
      ports:
        - containerPort: 80
```

**Pod 的设计哲学**：
- 单 Pod 单容器是最常见的模式
- 多容器 Pod 适用于紧密耦合的辅助进程（如日志收集、数据同步）
- Pod 是临时性的，不应直接依赖特定 Pod 的持久状态

### 3.2 Deployment

Deployment 用于管理无状态应用，支持声明式更新和滚动发布。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
```

常用操作：

```bash
# 创建 Deployment
kubectl apply -f deployment.yaml

# 查看滚动更新状态
kubectl rollout status deployment/nginx-deployment

# 版本回滚
kubectl rollout undo deployment/nginx-deployment

# 扩缩容
kubectl scale deployment nginx-deployment --replicas=5
```

### 3.3 Service

Service 为一组 Pod 提供稳定的网络端点，解决 Pod 动态 IP 变化的问题。

| Service 类型 | 说明 |
|-------------|------|
| ClusterIP | 默认类型，仅集群内部访问 |
| NodePort | 在每个节点开放端口，暴露到集群外部 |
| LoadBalancer | 云厂商负载均衡器，适用于云环境 |
| ExternalName | DNS 别名映射 |

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
```

### 3.4 ConfigMap 与 Secret

用于配置解耦和敏感信息管理：

```yaml
# ConfigMap：非敏感配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgres://db:5432/myapp"
  log_level: "info"

---
# Secret：敏感信息（Base64 编码）
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=      # admin
  password: cGFzc3dvcmQxMjM=  # password123
```

### 3.5 PersistentVolume（PV）与 PersistentVolumeClaim（PVC）

解决容器存储的持久化问题：

```yaml
# PVC 申请存储
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
# Pod 中使用 PVC
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  template:
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          volumeMounts:
            - name: data
              mountPath: /var/lib/mysql
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: mysql-pvc
```

## 四、Namespace 与资源隔离

Namespace 提供逻辑上的资源隔离，适用于多团队或多环境共享集群：

```bash
# 创建命名空间
kubectl create namespace dev

# 在指定命名空间操作资源
kubectl get pods -n dev
kubectl apply -f app.yaml -n dev

# 设置默认命名空间
kubectl config set-context --current --namespace=dev
```

常见命名空间划分策略：
- `default`：默认命名空间
- `kube-system`：K8s 系统组件
- `dev` / `test` / `prod`：按环境隔离
- `team-a` / `team-b`：按团队隔离

## 五、实战：部署一个完整的 Web 应用

以下示例展示如何部署一个完整的 Web 应用（Nginx + 共享存储）：

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: demo

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: demo
data:
  nginx.conf: |
    server {
      listen 80;
      location / {
        root /usr/share/nginx/html;
        index index.html;
      }
    }

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
          ports:
            - containerPort: 80
          volumeMounts:
            - name: config
              mountPath: /etc/nginx/conf.d
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "128Mi"
              cpu: "200m"
      volumes:
        - name: config
          configMap:
            name: nginx-config

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
  namespace: demo
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

部署命令：

```bash
kubectl apply -f namespace.yaml -f configmap.yaml -f deployment.yaml -f service.yaml

# 验证
kubectl get all -n demo
kubectl get svc -n demo
# 访问应用（假设节点 IP 为 192.168.1.100）
curl http://192.168.1.100:30080
```

## 六、常用 kubectl 命令速查

```bash
# 资源查看
kubectl get pods,svc,deploy -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name> -f
kubectl exec -it <pod-name> -- /bin/sh

# 资源操作
kubectl apply -f <yaml-file>
kubectl delete -f <yaml-file>
kubectl edit deployment <name>

# 调试诊断
kubectl top node              # 节点资源使用
kubectl top pod               # Pod 资源使用
kubectl port-forward svc/<name> 8080:80  # 本地端口转发

# 集群信息
kubectl cluster-info
kubectl get nodes -o wide
kubectl get events --sort-by='.lastTimestamp'
```

## 七、学习路径建议

1. **基础阶段**：理解 Pod、Deployment、Service 的核心概念
2. **进阶阶段**：掌握 ConfigMap/Secret、PV/PVC、RBAC 权限控制
3. **高级阶段**：学习 Helm 包管理、Ingress 流量管理、HPA 自动扩缩容
4. **专家阶段**：深入源码、自定义 CRD/Operator、多集群管理

## 结语

Kubernetes 的学习曲线虽然陡峭，但其带来的自动化能力和可扩展性是传统部署方式无法比拟的。建议读者从本地 Minikube 或 Kind 环境开始实践，逐步积累运维经验。掌握 K8s 不仅是技术能力的提升，更是云原生时代工程师的必备技能。

---

> **参考资源**：
> - [Kubernetes 官方文档](https://kubernetes.io/docs/)
> - [Kubernetes 中文社区](https://www.kubernetes.org.cn/)
> - 《Kubernetes in Action》— Marko Lukša
