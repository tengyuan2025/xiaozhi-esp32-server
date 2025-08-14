#!/bin/bash

# 简化版 Docker 启动脚本，避免复杂的健康检查

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 xiaozhi-esp32-server 简化启动脚本${NC}"
echo ""

# 检查 Docker
if ! command -v docker >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi

# 检查 Docker Compose
if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 环境检查通过${NC}"
echo -e "${BLUE}📋 使用命令: $COMPOSE_CMD${NC}"
echo ""

# 创建必要目录
mkdir -p config nginx/ssl mysql/conf.d
if [ ! -f "config/production.yaml" ]; then
    cat > config/production.yaml << EOF
# 生产环境配置
server:
  ip: 0.0.0.0
  port: 8000
  http_port: 8003
EOF
    echo -e "${GREEN}✅ 已创建配置文件模板${NC}"
fi

echo -e "${YELLOW}🔨 开始构建和启动服务...${NC}"
echo -e "${BLUE}💡 首次运行需要下载镜像，请耐心等待 5-10 分钟${NC}"
echo ""

# 启动服务，显示实时输出
$COMPOSE_CMD -f docker-compose.dev.yml up -d --build

# 简单等待
echo ""
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 10

# 检查状态
echo ""
echo -e "${BLUE}📊 当前服务状态:${NC}"
$COMPOSE_CMD -f docker-compose.dev.yml ps

echo ""
echo -e "${GREEN}🌐 服务访问地址:${NC}"
echo ""
echo -e "${YELLOW}核心服务:${NC}"
echo "  📡 xiaozhi-server:  http://localhost:8000 | http://localhost:8003"
echo "  🔧 manager-api:     http://localhost:8080"  
echo "  🖥️  manager-web:     http://localhost:8081"
echo "  📱 manager-mobile:  http://localhost:8082"
echo ""
echo -e "${YELLOW}统一入口:${NC}"
echo "  🏠 主页:            http://localhost/"
echo "  🎛️  Web管理界面:     http://localhost/admin/"
echo "  📲 移动端H5:        http://localhost/mobile/"
echo "  🔗 API接口:         http://localhost/api/"
echo "  ⚡ WebSocket:       ws://localhost:8000/xiaozhi/v1/"
echo ""

# 连接测试
echo -e "${BLUE}🧪 快速连接测试:${NC}"
for port in 8000 8003 8080 8081 8082; do
    if curl -s -f --connect-timeout 3 "http://localhost:$port/" >/dev/null 2>&1; then
        echo -e "  端口 $port: ${GREEN}✅ 可访问${NC}"
    else
        echo -e "  端口 $port: ${YELLOW}⏳ 还未就绪${NC}"
    fi
done

echo ""
echo -e "${BLUE}📝 常用命令:${NC}"
echo "  查看日志:         $COMPOSE_CMD -f docker-compose.dev.yml logs -f"
echo "  查看特定服务:     $COMPOSE_CMD -f docker-compose.dev.yml logs xiaozhi-server"
echo "  重启服务:        $COMPOSE_CMD -f docker-compose.dev.yml restart"
echo "  停止服务:        $COMPOSE_CMD -f docker-compose.dev.yml down"
echo "  查看状态:        ./check-status.sh"

echo ""
echo -e "${GREEN}🎉 启动完成！${NC}"
echo -e "${BLUE}💡 如果服务还未就绪，请等待 1-2 分钟后再次访问${NC}"