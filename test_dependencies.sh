#!/bin/bash

# xiaozhi-esp32-server 依赖检查脚本 (测试版本)
# 检查环境和依赖配置，但不实际安装

set -e  # 遇到错误时退出

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

# 检查命令是否存在
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

log_info "检查 xiaozhi-esp32-server 项目环境..."
log_info "项目根目录: $PROJECT_ROOT"

# 检查基础工具
echo ""
log_info "========== 检查基础工具 =========="

# Python
if check_command python3; then
    log_success "Python3: $(python3 --version)"
else
    log_error "Python3 未安装"
fi

if check_command pip3; then
    log_success "pip3: $(pip3 --version | head -n 1)"
else
    log_error "pip3 未安装"
fi

# Java
if check_command java; then
    log_success "Java: $(java -version 2>&1 | head -n 1)"
else
    log_error "Java 未安装"
fi

if check_command mvn; then
    log_success "Maven: $(mvn --version | head -n 1)"
else
    log_error "Maven 未安装"
fi

# Node.js
if check_command node; then
    log_success "Node.js: $(node --version)"
else
    log_error "Node.js 未安装"
fi

if check_command npm; then
    log_success "npm: $(npm --version)"
else
    log_error "npm 未安装"
fi

if check_command pnpm; then
    log_success "pnpm: $(pnpm --version)"
else
    log_warn "pnpm 未安装 (推荐安装: npm install -g pnpm)"
fi

# 检查项目结构
echo ""
log_info "========== 检查项目结构 =========="

components=(
    "main/xiaozhi-server:Python 核心服务"
    "main/manager-api:Java 管理 API"  
    "main/manager-web:Web 管理界面"
    "main/manager-mobile:移动端应用"
)

for component in "${components[@]}"; do
    dir="${component%:*}"
    name="${component#*:}"
    
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        log_success "$name: $dir ✓"
    else
        log_warn "$name: $dir 目录不存在"
    fi
done

# 检查依赖文件
echo ""
log_info "========== 检查依赖文件 =========="

dep_files=(
    "main/xiaozhi-server/requirements.txt:Python 依赖"
    "main/manager-api/pom.xml:Java 依赖"
    "main/manager-web/package.json:Web 前端依赖"
    "main/manager-mobile/package.json:移动端依赖"
)

for dep_file in "${dep_files[@]}"; do
    file="${dep_file%:*}"
    name="${dep_file#*:}"
    
    if [ -f "$PROJECT_ROOT/$file" ]; then
        log_success "$name: $file ✓"
    else
        log_warn "$name: $file 文件不存在"
    fi
done

# 检查配置文件
echo ""
log_info "========== 检查配置文件 =========="

config_files=(
    "main/xiaozhi-server/config.yaml:主配置文件"
    "main/xiaozhi-server/data/.config.yaml:本地配置覆盖"
)

for config_file in "${config_files[@]}"; do
    file="${config_file%:*}"
    name="${config_file#*:}"
    
    if [ -f "$PROJECT_ROOT/$file" ]; then
        log_success "$name: $file ✓"
    else
        log_warn "$name: $file 不存在"
    fi
done

# 生成安装建议
echo ""
log_info "========== 安装建议 =========="

missing_tools=()

if ! check_command python3; then
    missing_tools+=("Python3")
fi

if ! check_command java; then
    missing_tools+=("Java")
fi

if ! check_command mvn; then
    missing_tools+=("Maven")
fi

if ! check_command node; then
    missing_tools+=("Node.js")
fi

if [ ${#missing_tools[@]} -eq 0 ]; then
    log_success "所有必要工具都已安装，可以运行完整的依赖安装脚本:"
    echo ""
    echo -e "${GREEN}./install_dependencies.sh${NC}"
else
    log_warn "以下工具需要安装:"
    for tool in "${missing_tools[@]}"; do
        echo "  - $tool"
    done
    echo ""
    log_info "请先安装缺失的工具，然后运行完整的依赖安装脚本"
fi

echo ""
log_info "测试完成!"