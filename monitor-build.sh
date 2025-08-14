#!/bin/bash

# Docker 构建监控脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Docker 构建监控 ===${NC}"
echo "监控 Docker 构建进度，请保持耐心..."
echo ""

# 检查 docker compose 进程
check_build_progress() {
    local build_log="/tmp/xiaozhi_build.log"
    
    # 后台运行 docker compose，输出到日志文件
    docker compose -f docker-compose.dev.yml up -d --build > $build_log 2>&1 &
    local build_pid=$!
    
    echo -e "${YELLOW}构建进程 PID: $build_pid${NC}"
    echo "按 Ctrl+C 可以停止监控（不会停止构建）"
    echo ""
    
    # 监控循环
    local last_line=""
    while kill -0 $build_pid 2>/dev/null; do
        # 显示最后几行日志
        if [ -f "$build_log" ]; then
            current_line=$(tail -n 1 "$build_log" 2>/dev/null)
            if [ "$current_line" != "$last_line" ] && [ -n "$current_line" ]; then
                echo "[$(date +'%H:%M:%S')] $current_line"
                last_line="$current_line"
            fi
        fi
        
        # 检查容器状态
        running_containers=$(docker ps --format "{{.Names}}" | grep -c "xiaozhi" 2>/dev/null || echo 0)
        if [ $running_containers -gt 0 ]; then
            echo -e "${GREEN}✓ 已有 $running_containers 个容器启动${NC}"
        fi
        
        sleep 3
    done
    
    wait $build_pid
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ 构建完成！${NC}"
        
        # 显示最终状态
        echo ""
        echo -e "${BLUE}=== 最终服务状态 ===${NC}"
        docker compose -f docker-compose.dev.yml ps
        
        echo ""
        echo -e "${GREEN}🌐 访问地址：${NC}"
        echo "  📡 xiaozhi-server:  http://localhost:8000 | http://localhost:8003"
        echo "  🔧 manager-api:     http://localhost:8080"
        echo "  🖥️  manager-web:     http://localhost:8081"
        echo "  📱 manager-mobile:  http://localhost:8082"
        echo "  🏠 统一入口:        http://localhost/"
        
    else
        echo -e "${RED}❌ 构建失败，退出码: $exit_code${NC}"
        echo ""
        echo "查看完整日志:"
        echo "  cat $build_log"
        echo ""
        echo "手动排查:"
        echo "  docker compose -f docker-compose.dev.yml logs"
    fi
    
    # 清理临时日志文件
    rm -f "$build_log"
}

# 信号处理
trap 'echo -e "\n${YELLOW}监控已停止，但构建仍在继续...${NC}"; exit 0' INT TERM

# 开始监控
check_build_progress