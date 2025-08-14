#!/bin/bash

# xiaozhi-esp32-server Docker 一键启动脚本
# 支持开发环境和生产环境的快速部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "xiaozhi-esp32-server Docker 一键启动脚本"
    echo ""
    echo "用法: $0 [选项] [命令]"
    echo ""
    echo "命令:"
    echo "  dev       启动开发环境 (默认)"
    echo "  prod      启动生产环境"
    echo "  stop      停止所有服务"
    echo "  restart   重启服务"
    echo "  clean     清理容器和数据卷"
    echo "  logs      查看日志"
    echo "  status    查看服务状态"
    echo "  build     重新构建镜像"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -v, --verbose  详细输出"
    echo "  --no-build     不重新构建镜像"
    echo "  --force        强制执行操作"
    echo ""
    echo "示例:"
    echo "  $0 dev          # 启动开发环境"
    echo "  $0 prod         # 启动生产环境"
    echo "  $0 logs xiaozhi-server  # 查看 xiaozhi-server 日志"
    echo "  $0 clean --force        # 强制清理所有数据"
}

# 检查 Docker 环境
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi

    # 优先使用 docker compose（新版本）
    if docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    log_info "Docker 版本: $(docker --version)"
    log_info "Compose 命令: $COMPOSE_CMD"
}

# 获取 compose 文件路径
get_compose_file() {
    local env=$1
    if [ "$env" = "prod" ]; then
        echo "docker-compose.prod.yml"
    else
        echo "docker-compose.dev.yml"
    fi
}

# 启动服务
start_services() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)
    local build_flag=""

    log_info "启动 $env 环境..."

    if [ "$NO_BUILD" != "true" ]; then
        build_flag="--build"
    fi

    # 检查 compose 文件是否存在
    if [ ! -f "$compose_file" ]; then
        log_error "Docker Compose 文件不存在: $compose_file"
        exit 1
    fi

    # 创建必要的目录
    create_directories

    # 启动服务
    log_info "执行命令: $COMPOSE_CMD -f $compose_file up -d $build_flag"
    log_info "正在构建镜像和启动服务，首次运行可能需要5-10分钟..."
    
    if [ "$VERBOSE" = "true" ]; then
        $COMPOSE_CMD -f "$compose_file" up -d $build_flag
    else
        $COMPOSE_CMD -f "$compose_file" up -d $build_flag 2>&1 | while read line; do
            echo "[$(date +'%H:%M:%S')] $line"
        done
    fi

    # 等待服务启动
    log_info "等待服务启动..."
    sleep 3
    
    # 检查服务状态
    check_services_health $compose_file
    
    if [ $? -eq 0 ]; then
        log_success "$env 环境启动成功！"
        show_service_info $env
    else
        log_error "$env 环境启动失败"
        log_info "请查看服务状态："
        $COMPOSE_CMD -f "$compose_file" ps
        exit 1
    fi
}

# 停止服务
stop_services() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)

    log_info "停止 $env 环境服务..."

    if [ -f "$compose_file" ]; then
        $COMPOSE_CMD -f "$compose_file" down
        log_success "服务已停止"
    else
        log_warn "Docker Compose 文件不存在: $compose_file"
        # 尝试停止所有相关容器
        docker stop $(docker ps -q --filter "name=xiaozhi-*") 2>/dev/null || true
    fi
}

# 重启服务
restart_services() {
    local env=${1:-dev}
    log_info "重启 $env 环境..."
    stop_services $env
    sleep 2
    start_services $env
}

# 清理服务
clean_services() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)
    local force_flag=""

    if [ "$FORCE" = "true" ]; then
        force_flag="-v"
    else
        log_warn "此操作将删除所有容器、网络和数据卷"
        read -p "确认继续吗? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            exit 0
        fi
    fi

    log_info "清理 $env 环境..."

    if [ -f "$compose_file" ]; then
        $COMPOSE_CMD -f "$compose_file" down $force_flag --remove-orphans
    fi

    # 清理相关容器和镜像
    docker container prune -f
    docker network prune -f
    
    if [ "$FORCE" = "true" ]; then
        docker volume prune -f
        # 清理构建的镜像
        docker image rm $(docker images -q --filter "reference=xiaozhi-esp32-server*") 2>/dev/null || true
    fi

    log_success "清理完成"
}

# 查看日志
show_logs() {
    local env=${1:-dev}
    local service=$2
    local compose_file=$(get_compose_file $env)

    if [ -f "$compose_file" ]; then
        if [ -n "$service" ]; then
            log_info "查看 $service 服务日志..."
            $COMPOSE_CMD -f "$compose_file" logs -f "$service"
        else
            log_info "查看所有服务日志..."
            $COMPOSE_CMD -f "$compose_file" logs -f
        fi
    else
        log_error "Docker Compose 文件不存在: $compose_file"
        exit 1
    fi
}

# 查看服务状态
show_status() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)

    if [ -f "$compose_file" ]; then
        log_info "服务状态:"
        $COMPOSE_CMD -f "$compose_file" ps
    else
        log_warn "Docker Compose 文件不存在，显示相关容器状态:"
        docker ps --filter "name=xiaozhi-*"
    fi
}

# 重新构建镜像
build_images() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)

    log_info "重新构建 $env 环境镜像..."

    if [ -f "$compose_file" ]; then
        $COMPOSE_CMD -f "$compose_file" build --no-cache
        log_success "镜像构建完成"
    else
        log_error "Docker Compose 文件不存在: $compose_file"
        exit 1
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p config nginx/ssl mysql/conf.d
    
    # 创建生产环境配置模板
    if [ ! -f "config/production.yaml" ]; then
        cat > config/production.yaml << EOF
# 生产环境配置
server:
  ip: 0.0.0.0
  port: 8000
  http_port: 8003

log:
  log_level: INFO
  log_dir: logs
  log_file: "server.log"

# 请在此处添加你的生产环境配置
# 例如 API 密钥、数据库连接等
EOF
        log_info "已创建生产环境配置模板: config/production.yaml"
    fi
}

# 检查服务健康状态
check_services_health() {
    local compose_file=$1
    local max_wait=120  # 最大等待2分钟
    local wait_time=0
    local services_ready=false
    
    log_info "检查服务健康状态..."
    
    while [ $wait_time -lt $max_wait ] && [ "$services_ready" = false ]; do
        # 检查容器状态 - 使用更简单的方法
        running_containers=$($COMPOSE_CMD -f "$compose_file" ps -q 2>/dev/null | wc -l | tr -d ' ')
        healthy_containers=$($COMPOSE_CMD -f "$compose_file" ps --filter "status=running" -q 2>/dev/null | wc -l | tr -d ' ')
        
        # 确保变量是数字
        running_containers=${running_containers:-0}
        healthy_containers=${healthy_containers:-0}
        
        log_info "运行中的容器: $healthy_containers/$running_containers (等待时间: ${wait_time}s)"
        
        # 检查是否有足够的服务运行
        if [ "$healthy_containers" -ge 3 ] 2>/dev/null; then
            services_ready=true
            break
        fi
        
        sleep 5
        wait_time=$((wait_time + 5))
    done
    
    if [ "$services_ready" = true ]; then
        return 0
    else
        return 1
    fi
}

# 显示服务信息
show_service_info() {
    local env=$1
    
    echo ""
    log_success "========== 服务访问信息 =========="
    
    # 显示当前运行的服务
    log_info "当前运行的服务:"
    if [ "$env" = "dev" ]; then
        compose_file="docker-compose.dev.yml"
    else
        compose_file="docker-compose.prod.yml"
    fi
    
    $COMPOSE_CMD -f "$compose_file" ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}"
    
    echo ""
    if [ "$env" = "dev" ]; then
        echo "🌐 开发环境访问地址:"
        echo ""
        echo "核心服务："
        echo "  📡 xiaozhi-server (Python核心):  http://localhost:8000 | http://localhost:8003"
        echo "  🔧 manager-api (Java后端):      http://localhost:8080"
        echo "  🖥️  manager-web (Web管理):       http://localhost:8081"
        echo "  📱 manager-mobile (移动端):     http://localhost:8082"
        echo ""
        echo "统一访问入口："
        echo "  🏠 主页:                        http://localhost/"
        echo "  🎛️  Web管理界面:                 http://localhost/admin/"
        echo "  📲 移动端H5:                    http://localhost/mobile/"
        echo "  🔗 API接口:                     http://localhost/api/"
        echo "  ⚡ WebSocket服务:               ws://localhost:8000/xiaozhi/v1/"
        echo ""
        echo "数据库连接:"
        echo "  🗄️  MySQL:                      localhost:3306 (xiaozhi/xiaozhi123)"
        echo "  ⚡ Redis:                       localhost:6379 (password: xiaozhi123)"
    else
        echo "🏭 生产环境访问地址:"
        echo "  🏠 统一入口:                    http://localhost/"
        echo "  🔒 HTTPS访问:                   https://localhost/ (需配置SSL)"
        echo ""
        echo "管理入口:"
        echo "  🎛️  Web管理:                    http://localhost/admin/"
        echo "  📲 移动端:                      http://localhost/mobile/"
        echo "  🔗 API接口:                     http://localhost/api/"
    fi
    
    echo ""
    log_info "📋 常用操作命令:"
    echo "  查看实时日志:  $0 logs [service_name]"
    echo "  查看服务状态:  $0 status"
    echo "  重启服务:     $0 restart $env"
    echo "  停止服务:     $0 stop $env"
    echo ""
    log_info "🧪 快速测试:"
    echo "  curl http://localhost:8003/     # 测试Python服务"
    echo "  curl http://localhost:8080/     # 测试Java API"
    echo "  curl http://localhost/          # 测试统一入口"
}

# 解析命令行参数
COMMAND="dev"
ENV="dev"
VERBOSE=false
NO_BUILD=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-build)
            NO_BUILD=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        dev|prod|stop|restart|clean|logs|status|build)
            COMMAND=$1
            if [[ "$COMMAND" == "prod" ]]; then
                ENV="prod"
                COMMAND="start"
            elif [[ "$COMMAND" == "dev" ]]; then
                ENV="dev"
                COMMAND="start"
            fi
            shift
            ;;
        *)
            # 额外参数（如服务名称）
            SERVICE_NAME=$1
            shift
            ;;
    esac
done

# 主程序
main() {
    log_info "xiaozhi-esp32-server Docker 管理脚本"
    
    # 检查 Docker 环境
    check_docker
    
    # 执行相应命令
    case $COMMAND in
        start)
            start_services $ENV
            ;;
        stop)
            stop_services $ENV
            ;;
        restart)
            restart_services $ENV
            ;;
        clean)
            clean_services $ENV
            ;;
        logs)
            show_logs $ENV $SERVICE_NAME
            ;;
        status)
            show_status $ENV
            ;;
        build)
            build_images $ENV
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 执行主程序
main "$@"