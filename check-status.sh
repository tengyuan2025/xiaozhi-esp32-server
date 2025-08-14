#!/bin/bash

# 快速检查 Docker 服务状态脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== xiaozhi-esp32-server 服务状态检查 ===${NC}"
echo ""

# 检查 Docker Compose 服务
if [ -f "docker-compose.dev.yml" ]; then
    echo -e "${YELLOW}Docker Compose 服务状态:${NC}"
    docker compose -f docker-compose.dev.yml ps 2>/dev/null || echo "Docker Compose 未运行"
    echo ""
fi

# 检查相关容器
echo -e "${YELLOW}相关容器状态:${NC}"
docker ps -a --filter "name=xiaozhi" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "未找到相关容器"
echo ""

# 检查端口占用
echo -e "${YELLOW}端口占用检查:${NC}"
for port in 80 8000 8003 8080 8081 8082 3306 6379; do
    if lsof -i :$port >/dev/null 2>&1; then
        process=$(lsof -i :$port | tail -n 1 | awk '{print $1}')
        echo -e "  端口 $port: ${GREEN}使用中${NC} ($process)"
    else
        echo -e "  端口 $port: ${RED}空闲${NC}"
    fi
done
echo ""

# 快速连接测试
echo -e "${YELLOW}服务连接测试:${NC}"
services=(
    "8003:xiaozhi-server HTTP"
    "8080:manager-api"
    "8081:manager-web"
    "8082:manager-mobile"
    "80:nginx统一入口"
)

for service in "${services[@]}"; do
    port="${service%:*}"
    name="${service#*:}"
    if curl -s -f "http://localhost:$port/" >/dev/null 2>&1; then
        echo -e "  $name: ${GREEN}✓ 可访问${NC} (http://localhost:$port/)"
    else
        echo -e "  $name: ${RED}✗ 不可访问${NC} (http://localhost:$port/)"
    fi
done
echo ""

# 显示日志命令提示
echo -e "${BLUE}常用调试命令:${NC}"
echo "  查看所有日志:     docker compose -f docker-compose.dev.yml logs"
echo "  查看特定服务:     docker compose -f docker-compose.dev.yml logs xiaozhi-server"
echo "  实时跟踪日志:     docker compose -f docker-compose.dev.yml logs -f"
echo "  重启服务:        ./docker-start.sh restart dev"
echo "  完全重建:        ./docker-start.sh clean --force && ./docker-start.sh dev"