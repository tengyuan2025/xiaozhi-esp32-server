# 开发环境配置文档

本文档提供 xiaozhi-esp32-server 项目的开发环境配置和依赖安装指南。

## 快速开始

### 🐳 Docker 一键部署（推荐）

项目提供了完整的 Docker 化环境，无需手动安装任何依赖：

```bash
# 克隆项目后，在项目根目录执行
./docker-start.sh dev
```

该命令将自动：
- 构建所有服务的 Docker 镜像
- 启动 MySQL、Redis、Python 服务、Java API、Web 界面等全部组件
- 配置服务间的网络连接和数据卷
- 提供统一的访问入口

**Docker 环境访问地址：**
- 统一入口：http://localhost/
- Web 管理界面：http://localhost/admin/
- 移动端 H5：http://localhost/mobile/
- WebSocket 服务：ws://localhost:8000/xiaozhi/v1/

### 📦 传统方式安装依赖

如果不使用 Docker，也可以通过传统方式安装依赖：

```bash
# 在项目根目录执行
./install_dependencies.sh
```

该脚本将自动：
- 检测系统环境和必要工具
- 安装 Python、Java、Node.js 等各组件依赖
- 创建必要的目录结构
- 生成配置文件模板
- 记录详细的安装日志

## 系统要求

### Docker 环境（推荐）

| 工具 | 最低版本 | 推荐版本 | 安装方式 |
|-----|---------|---------|---------|
| **Docker** | 20.0+ | 24.0+ | [docker.com](https://docker.com/get-started) |
| **Docker Compose** | 2.0+ | 2.20+ | 包含在 Docker Desktop 中 |

### 传统开发环境

| 工具 | 最低版本 | 推荐版本 | 安装方式 |
|-----|---------|---------|---------|
| **Python** | 3.8+ | 3.11+ | [python.org](https://python.org) |
| **Java** | 17+ | 21+ | [OpenJDK](https://openjdk.org) |
| **Node.js** | 16+ | 18+ | [nodejs.org](https://nodejs.org) |
| **Maven** | 3.6+ | 3.9+ | [maven.apache.org](https://maven.apache.org) |

### 包管理器

- **Python**: pip3 (通常与 Python 一起安装)
- **Java**: Maven (需单独安装)
- **Node.js**: npm (与 Node.js 一起安装) 或 pnpm (推荐)

### 可选工具

```bash
# 安装 pnpm (推荐用于移动端开发)
npm install -g pnpm

# 安装 FFmpeg (音频处理)
# macOS
brew install ffmpeg
# Ubuntu
sudo apt install ffmpeg
# CentOS
sudo yum install ffmpeg
```

## 项目结构和依赖

### 1. xiaozhi-server (Python 核心服务)

**位置**: `main/xiaozhi-server/`

**主要依赖**:
```
torch==2.2.2              # 深度学习框架
funasr==1.2.3             # 语音识别
openai==1.61.0            # OpenAI API
websockets==14.2          # WebSocket 服务器
aiohttp==3.9.3            # HTTP 异步客户端
silero_vad==5.1.2         # 语音活动检测
edge_tts==7.0.0           # 微软 TTS
mem0ai==0.1.62            # 记忆系统
mcp==1.8.1                # MCP 协议
```

**安装命令**:
```bash
cd main/xiaozhi-server
pip3 install -r requirements.txt
```

**启动服务**:
```bash
python app.py
```

### 2. manager-api (Java 管理后端)

**位置**: `main/manager-api/`

**技术栈**:
- Spring Boot 3.4.3
- Java 21
- MyBatis Plus 3.5.5
- Apache Shiro 2.0.2
- MySQL + Redis

**安装命令**:
```bash
cd main/manager-api
mvn clean dependency:resolve
```

**启动服务**:
```bash
mvn spring-boot:run
# 或者
java -jar target/xiaozhi-esp32-api.jar
```

### 3. manager-web (Vue2 Web 管理界面)

**位置**: `main/manager-web/`

**技术栈**:
- Vue 2.6.14
- Element UI 2.15.14
- Vue Router 3.6.5
- Vuex 3.6.2

**安装命令**:
```bash
cd main/manager-web
npm install
```

**开发启动**:
```bash
npm run serve      # 开发模式
npm run build      # 生产构建
npm run analyze    # 分析包大小
```

### 4. manager-mobile (Uni-app 移动端)

**位置**: `main/manager-mobile/`

**技术栈**:
- Uni-app (支持多端发布)
- Vue 3.4.21
- TypeScript
- Vite 5.2.8
- UnoCSS

**安装命令**:
```bash
cd main/manager-mobile
pnpm install  # 推荐使用 pnpm
# 或者
npm install
```

**开发启动**:
```bash
# H5 开发
pnpm run dev:h5

# 微信小程序
pnpm run dev:mp-weixin

# Android App
pnpm run build:app-android

# 类型检查
pnpm run type-check

# 代码检查和修复
pnpm run lint:fix
```

## 开发环境配置

### 1. Python 服务配置

创建本地配置文件 `main/xiaozhi-server/data/.config.yaml`:

```yaml
# 本地开发配置
selected_module:
  ASR: FunASR          # 语音识别
  LLM: ChatGLMLLM      # 大语言模型
  TTS: EdgeTTS         # 语音合成
  VLLM: ChatGLMVLLM    # 视觉语言模型

# API 密钥配置
LLM:
  ChatGLMLLM:
    api_key: 你的智谱API密钥

# 服务器配置
server:
  ip: 0.0.0.0
  port: 8000
  http_port: 8003
```

### 2. 数据库配置

Java API 需要 MySQL 数据库，在 `main/manager-api/src/main/resources/application-dev.yml` 中配置：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/xiaozhi
    username: your_username
    password: your_password
  redis:
    host: localhost
    port: 6379
```

### 3. 环境变量

可选的环境变量配置：

```bash
# Python 服务
export XIAOZHI_CONFIG_PATH=/path/to/your/config.yaml
export XIAOZHI_LOG_LEVEL=DEBUG

# Java API
export SPRING_PROFILES_ACTIVE=dev
export SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3306/xiaozhi

# Web 前端
export VUE_APP_API_BASE_URL=http://localhost:8080
```

## Docker 开发工作流（推荐）

### 1. 一键启动所有服务

```bash
# 启动开发环境
./docker-start.sh dev

# 或者启动生产环境
./docker-start.sh prod
```

### 2. 常用 Docker 命令

```bash
# 查看服务状态
./docker-start.sh status

# 查看所有日志
./docker-start.sh logs

# 查看特定服务日志
./docker-start.sh logs xiaozhi-server

# 重启服务
./docker-start.sh restart dev

# 停止服务
./docker-start.sh stop

# 清理所有容器和数据
./docker-start.sh clean --force

# 重新构建镜像
./docker-start.sh build
```

### 3. Docker 环境访问地址

- **统一入口**: `http://localhost/`
- **Web 管理界面**: `http://localhost/admin/`
- **移动端 H5**: `http://localhost/mobile/`
- **API 接口**: `http://localhost/api/`
- **WebSocket 服务**: `ws://localhost:8000/xiaozhi/v1/`
- **直接访问各服务**:
  - xiaozhi-server: `http://localhost:8000` / `http://localhost:8003`
  - manager-api: `http://localhost:8080`
  - manager-web: `http://localhost:8081`
  - manager-mobile: `http://localhost:8082`

## 传统开发工作流

### 1. 启动开发环境

```bash
# 1. 启动 Python 核心服务
cd main/xiaozhi-server
python app.py

# 2. 启动 Java 管理 API (新终端)
cd main/manager-api
mvn spring-boot:run

# 3. 启动 Web 管理界面 (新终端)
cd main/manager-web
npm run serve

# 4. 启动移动端开发 (新终端, 可选)
cd main/manager-mobile
pnpm run dev:h5
```

### 2. 传统环境访问地址

- **WebSocket 服务**: `ws://localhost:8000/xiaozhi/v1/`
- **HTTP API**: `http://localhost:8003/`
- **管理 API**: `http://localhost:8080/`
- **Web 管理界面**: `http://localhost:8081/`
- **移动端 H5**: `http://localhost:5173/`

### 3. 测试功能

```bash
# Python 服务性能测试
cd main/xiaozhi-server
python performance_test_tool.py

# 音频功能测试
# 使用 Chrome 浏览器打开 main/xiaozhi-server/test/test_page.html

# Java API 测试
cd main/manager-api
mvn test
```

## 常见问题和解决方案

### 1. Python 依赖安装失败

```bash
# 升级 pip
python3 -m pip install --upgrade pip

# 使用国内镜像源
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 如果 torch 安装失败，单独安装
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. Node.js 依赖安装失败

```bash
# 清理缓存
npm cache clean --force

# 删除 node_modules 重新安装
rm -rf node_modules package-lock.json
npm install

# 使用国内镜像源
npm config set registry https://registry.npmmirror.com
```

### 3. Java 依赖下载缓慢

在 `main/manager-api/pom.xml` 中已配置阿里云 Maven 仓库，如仍然缓慢可配置本地 Maven 设置：

```xml
<!-- ~/.m2/settings.xml -->
<mirrors>
  <mirror>
    <id>aliyun</id>
    <mirrorOf>central</mirrorOf>
    <url>https://maven.aliyun.com/repository/central</url>
  </mirror>
</mirrors>
```

### 4. 端口冲突

如果默认端口被占用，可以修改配置：

```yaml
# Python 服务端口
server:
  port: 8001          # WebSocket 端口
  http_port: 8004     # HTTP 端口
```

```bash
# Web 前端端口
npm run serve -- --port 8082

# 移动端端口
pnpm run dev:h5 -- --port 5174
```

## Docker 环境详细配置

### 部署选项

项目提供了两套 Docker 环境：

#### 开发环境 (docker-compose.dev.yml)
- **特点**: 开发友好，支持代码热更新
- **资源**: 较少的资源限制，便于调试
- **数据**: 数据卷持久化，便于开发测试
- **启动**: `./docker-start.sh dev`

#### 生产环境 (docker-compose.prod.yml)
- **特点**: 优化的生产配置
- **资源**: 严格的资源限制和安全设置
- **数据**: 完整的数据持久化
- **启动**: `./docker-start.sh prod`

### 环境变量配置

生产环境支持环境变量配置：

```bash
# .env 文件示例
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_PASSWORD=your_secure_password  
REDIS_PASSWORD=your_secure_redis_password
```

### 数据卷说明

- `mysql_data`: MySQL 数据库文件
- `redis_data`: Redis 数据文件
- `xiaozhi_models`: AI 模型文件
- `xiaozhi_tmp`: 临时文件
- `xiaozhi_data`: 应用数据
- `xiaozhi_logs`: 日志文件

### 网络配置

- **开发环境**: `172.20.0.0/16`
- **生产环境**: `172.21.0.0/16`
- **服务发现**: 容器间通过服务名通信

### Docker 部署命令

```bash
# 快速启动开发环境
./docker-start.sh dev

# 启动生产环境
./docker-start.sh prod

# 查看运行状态
./docker-start.sh status

# 查看日志
./docker-start.sh logs

# 单独构建镜像
docker build -f Dockerfile.xiaozhi-server -t xiaozhi-server .
docker build -f Dockerfile.manager-api -t manager-api .
docker build -f Dockerfile.manager-web -t manager-web .
docker build -f Dockerfile.manager-mobile -t manager-mobile .
```

### 传统部署方式

如果不使用 Docker，可以使用传统方式构建：

```bash
# Web 前端构建
cd main/manager-web
npm run build

# 移动端构建
cd main/manager-mobile
pnpm run build:h5

# Java API 构建
cd main/manager-api
mvn clean package
```

## 开发工具推荐

### IDE 配置

- **Python**: PyCharm, VSCode + Python 插件
- **Java**: IntelliJ IDEA, VSCode + Java 插件  
- **前端**: VSCode + Vetur + ESLint
- **移动端**: HBuilderX, VSCode + Uni-app 插件

### 有用的 VSCode 插件

```json
{
  "recommendations": [
    "ms-python.python",
    "redhat.java",
    "octref.vetur",
    "uni-helper.uni-app-schemas",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode"
  ]
}
```

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 更新日志

### v1.0.0 (2025-01-14)
- 初始版本发布
- 添加自动化依赖安装脚本
- 完善开发环境配置文档

### 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues: https://github.com/xinnan-tech/xiaozhi-esp32-server/issues
- 项目文档: 查看 `docs/` 目录下的相关文档