# 🐳 Docker 部署指南

本文档专门介绍如何使用 Docker 来部署 xiaozhi-esp32-server 项目，确保在任何环境下都能获得一致的运行体验。

## 为什么选择 Docker？

✅ **环境一致性**: 无论在什么系统上，都能获得相同的运行环境  
✅ **依赖隔离**: 所有依赖都封装在容器中，不会影响宿主机  
✅ **一键部署**: 无需手动安装 Python、Java、Node.js 等工具链  
✅ **快速启动**: 几分钟内就能启动完整的系统  
✅ **易于维护**: 统一的容器化管理，便于运维和扩展  

## 快速开始

### 1. 安装 Docker

首先确保你的系统已安装 Docker：

**Windows/macOS:**
- 下载安装 [Docker Desktop](https://docs.docker.com/desktop/)

**Linux (Ubuntu):**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到 docker 组
sudo usermod -aG docker $USER
```

### 2. 克隆项目

```bash
git clone https://github.com/xinnan-tech/xiaozhi-esp32-server.git
cd xiaozhi-esp32-server
```

### 3. 一键启动

```bash
# 启动开发环境（推荐初次使用）
./docker-start.sh dev

# 或启动生产环境
./docker-start.sh prod
```

第一次运行会自动：
- 下载必要的基础镜像
- 构建所有服务镜像
- 创建网络和数据卷
- 启动所有容器

## 访问服务

启动完成后，你可以通过以下地址访问各个服务：

### 🌐 统一入口 (推荐)
- **主页**: http://localhost/
- **Web 管理界面**: http://localhost/admin/
- **移动端 H5**: http://localhost/mobile/
- **API 接口**: http://localhost/api/

### 🔗 直接访问各服务
- **WebSocket 服务**: ws://localhost:8000/xiaozhi/v1/
- **Python HTTP API**: http://localhost:8003/
- **Java 管理 API**: http://localhost:8080/
- **Web 管理界面**: http://localhost:8081/
- **移动端 H5**: http://localhost:8082/

## 常用操作

### 服务管理

```bash
# 查看服务状态
./docker-start.sh status

# 查看所有服务日志
./docker-start.sh logs

# 查看特定服务日志
./docker-start.sh logs xiaozhi-server
./docker-start.sh logs manager-api
./docker-start.sh logs manager-web

# 重启服务
./docker-start.sh restart dev

# 停止所有服务
./docker-start.sh stop

# 重新构建镜像（代码更新后）
./docker-start.sh build
```

### 数据管理

```bash
# 查看数据卷
docker volume ls | grep xiaozhi

# 备份数据
docker run --rm -v xiaozhi-esp32-server_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql-backup.tar.gz -C /data .

# 恢复数据
docker run --rm -v xiaozhi-esp32-server_mysql_data:/data -v $(pwd):/backup alpine tar xzf /backup/mysql-backup.tar.gz -C /data
```

### 清理操作

```bash
# 清理容器（保留数据）
./docker-start.sh stop
docker container prune -f

# 完全清理（包括数据）
./docker-start.sh clean --force

# 清理未使用的镜像
docker image prune -f
```

## 开发模式

Docker 环境也支持开发模式，可以实时修改代码：

### 开发环境特性

- **代码挂载**: 源代码目录挂载到容器中
- **热重载**: 修改代码后自动重启服务
- **调试友好**: 可以直接访问各个服务端口
- **资源宽松**: 较少的资源限制

### 开发工作流

```bash
# 启动开发环境
./docker-start.sh dev

# 修改代码
vim main/xiaozhi-server/app.py

# 查看日志确认重启
./docker-start.sh logs xiaozhi-server

# 测试功能
curl http://localhost:8003/
```

## 生产环境

生产环境配置经过优化，适合实际部署：

### 生产环境特性

- **资源限制**: 严格的 CPU 和内存限制
- **安全加固**: 安全头、权限控制等
- **性能优化**: 启用 gzip、缓存等
- **监控就绪**: 健康检查、日志输出等

### 生产环境配置

```bash
# 创建环境变量文件
cat > .env << EOF
MYSQL_ROOT_PASSWORD=your_super_secure_password_2024
MYSQL_PASSWORD=your_mysql_password_2024
REDIS_PASSWORD=your_redis_password_2024
EOF

# 启动生产环境
./docker-start.sh prod
```

## 服务架构

Docker 环境包含以下服务：

```
┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │     MySQL       │
│ (反向代理/负载均衡) │    │    (数据库)      │
└─────────────────┘    └─────────────────┘
         │                       │
    ┌────┴────┐                  │
    │         │                  │
┌───▼───┐ ┌──▼──┐            ┌───▼───┐
│ Web   │ │ H5  │            │ Redis │
│管理界面 │ │移动端 │            │ (缓存) │
└───────┘ └─────┘            └───────┘
         │                       │
    ┌────┴────┐                  │
    │         │                  │
┌───▼───┐ ┌──▼──────────────────▼───┐
│Python │ │        Java            │
│核心服务 │ │      管理 API           │
└───────┘ └────────────────────────┘
```

### 网络通信

- **外部访问**: 通过 Nginx (80/443 端口)
- **内部通信**: 容器间通过服务名通信
- **数据库**: MySQL + Redis 集群
- **负载均衡**: Nginx 反向代理

## 故障排查

### 常见问题

#### 1. 容器启动失败

```bash
# 查看详细日志
./docker-start.sh logs [service_name]

# 查看容器状态
docker ps -a | grep xiaozhi

# 重启特定服务
docker restart xiaozhi-server
```

#### 2. 端口冲突

```bash
# 查看端口占用
netstat -tlnp | grep :80
lsof -i :8080

# 停止冲突服务或修改端口配置
```

#### 3. 内存不足

```bash
# 查看资源使用
docker stats

# 清理未使用的容器和镜像
docker system prune -f
```

#### 4. 数据库连接失败

```bash
# 检查 MySQL 容器状态
docker logs xiaozhi-mysql

# 测试数据库连接
docker exec -it xiaozhi-mysql mysql -uxiaozhi -p
```

### 日志查看

```bash
# 实时查看所有日志
./docker-start.sh logs

# 查看特定服务日志
./docker-start.sh logs xiaozhi-server
./docker-start.sh logs manager-api

# 查看最近的日志
docker logs --tail 50 xiaozhi-server

# 查看历史日志
docker logs --since="2024-01-01T00:00:00" xiaozhi-server
```

## 高级配置

### 自定义配置

你可以通过挂载配置文件来自定义服务配置：

```bash
# 创建自定义配置目录
mkdir -p config

# 创建 Python 服务配置
cat > config/xiaozhi-server.yaml << EOF
server:
  ip: 0.0.0.0
  port: 8000

selected_module:
  LLM: ChatGLMLLM
  TTS: EdgeTTS

LLM:
  ChatGLMLLM:
    api_key: your_api_key_here
EOF

# 重启服务使配置生效
./docker-start.sh restart dev
```

### SSL/HTTPS 配置

```bash
# 创建 SSL 证书目录
mkdir -p nginx/ssl

# 放置证书文件
cp your-cert.pem nginx/ssl/
cp your-key.pem nginx/ssl/

# 修改 nginx 配置启用 HTTPS
# 然后重启服务
./docker-start.sh restart prod
```

### 性能调优

```bash
# 调整 Java 服务 JVM 参数
export JAVA_OPTS="-Xms2g -Xmx4g -XX:+UseG1GC"

# 调整 Python 服务工作进程数
export WORKERS=4

# 重新启动服务
./docker-start.sh restart prod
```

## 监控和运维

### 健康检查

所有服务都配置了健康检查：

```bash
# 查看健康状态
docker ps --format "table {{.Names}}\t{{.Status}}"

# 手动执行健康检查
docker exec xiaozhi-server curl -f http://localhost:8003/
```

### 备份策略

```bash
# 自动备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/xiaozhi-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份数据库
docker exec xiaozhi-mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD xiaozhi > $BACKUP_DIR/mysql.sql

# 备份 Redis
docker exec xiaozhi-redis redis-cli --rdb $BACKUP_DIR/redis.rdb

# 备份应用数据
docker run --rm -v xiaozhi-esp32-server_xiaozhi_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/app-data.tar.gz -C /data .

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh
./backup.sh
```

---

## 总结

通过 Docker 部署 xiaozhi-esp32-server 项目具有以下优势：

1. **简单快捷**: 一个命令即可启动完整系统
2. **环境一致**: 开发、测试、生产环境完全一致
3. **易于维护**: 统一的容器化管理
4. **快速扩展**: 支持横向扩展和负载均衡
5. **故障隔离**: 各服务独立运行，互不影响

如果你在使用过程中遇到问题，请查看项目的 [Issues](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues) 或提交新的问题。