#!/bin/bash

echo "==================================="
echo "小智 MySQL & Redis 服务启动脚本"
echo "==================================="

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker Desktop"
    exit 1
fi

echo "✅ Docker 服务正常运行"

# 停止已有容器（如果存在）
echo "🔄 停止已有容器..."
docker-compose down

# 启动服务
echo "🚀 启动 MySQL 和 Redis 服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动完成..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 检查 MySQL 连接
echo "🔍 测试 MySQL 连接..."
until docker exec xiaozhi-mysql mysqladmin ping -h"localhost" --silent; do
    echo "   等待 MySQL 启动..."
    sleep 2
done
echo "✅ MySQL 服务已就绪"

# 检查 Redis 连接
echo "🔍 测试 Redis 连接..."
until docker exec xiaozhi-redis redis-cli ping | grep -q PONG; do
    echo "   等待 Redis 启动..."
    sleep 2
done
echo "✅ Redis 服务已就绪"

echo ""
echo "🎉 所有服务启动成功！"
echo ""
echo "📝 连接信息："
echo "   MySQL: localhost:3306"
echo "   数据库: xiaozhi_esp32_server"
echo "   用户: root / 密码: 123456"
echo "   Redis: localhost:6380"
echo ""
echo "🔧 管理命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""