#!/bin/bash

# xiaozhi-esp32-server 依赖安装脚本
# 自动安装所有组件的依赖并记录日志

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

# 创建日志文件
LOG_FILE="$PROJECT_ROOT/dependency_install.log"
echo "依赖安装日志 - $(date)" > "$LOG_FILE"

log_info "开始安装 xiaozhi-esp32-server 项目依赖..."
log_info "项目根目录: $PROJECT_ROOT"

# 1. 检查并安装 Python 依赖 (xiaozhi-server)
log_info "========== 安装 Python 依赖 (xiaozhi-server) =========="
PYTHON_DIR="$PROJECT_ROOT/main/xiaozhi-server"

if [ -d "$PYTHON_DIR" ]; then
    cd "$PYTHON_DIR"
    
    # 检查 Python 和 pip
    if ! check_command python3; then
        log_error "Python3 未安装，请先安装 Python3"
        exit 1
    fi
    
    if ! check_command pip3; then
        log_error "pip3 未安装，请先安装 pip3"
        exit 1
    fi
    
    log_info "Python 版本: $(python3 --version)"
    log_info "pip 版本: $(pip3 --version)"
    
    if [ -f "requirements.txt" ]; then
        log_info "安装 Python 依赖..."
        echo "Python 依赖安装开始 - $(date)" >> "$LOG_FILE"
        
        # 升级 pip
        python3 -m pip install --upgrade pip >> "$LOG_FILE" 2>&1
        
        # 安装依赖
        python3 -m pip install -r requirements.txt >> "$LOG_FILE" 2>&1
        
        log_success "Python 依赖安装完成"
        echo "Python 依赖安装完成 - $(date)" >> "$LOG_FILE"
    else
        log_warn "未找到 requirements.txt"
    fi
else
    log_warn "xiaozhi-server 目录不存在，跳过 Python 依赖安装"
fi

# 2. 检查并安装 Java 依赖 (manager-api)
log_info "========== 安装 Java 依赖 (manager-api) =========="
JAVA_DIR="$PROJECT_ROOT/main/manager-api"

if [ -d "$JAVA_DIR" ]; then
    cd "$JAVA_DIR"
    
    # 检查 Maven
    if ! check_command mvn; then
        log_error "Maven 未安装，请先安装 Maven"
        log_info "可以通过以下方式安装 Maven:"
        log_info "  - macOS: brew install maven"
        log_info "  - Ubuntu: sudo apt install maven"
        log_info "  - CentOS: sudo yum install maven"
        exit 1
    fi
    
    # 检查 Java
    if ! check_command java; then
        log_error "Java 未安装，请先安装 Java 21"
        exit 1
    fi
    
    log_info "Java 版本: $(java -version 2>&1 | head -n 1)"
    log_info "Maven 版本: $(mvn --version | head -n 1)"
    
    if [ -f "pom.xml" ]; then
        log_info "安装 Java 依赖..."
        echo "Java 依赖安装开始 - $(date)" >> "$LOG_FILE"
        
        # 清理并下载依赖
        mvn clean dependency:resolve >> "$LOG_FILE" 2>&1
        
        log_success "Java 依赖安装完成"
        echo "Java 依赖安装完成 - $(date)" >> "$LOG_FILE"
    else
        log_warn "未找到 pom.xml"
    fi
else
    log_warn "manager-api 目录不存在，跳过 Java 依赖安装"
fi

# 3. 检查并安装 Web 前端依赖 (manager-web)
log_info "========== 安装 Web 前端依赖 (manager-web) =========="
WEB_DIR="$PROJECT_ROOT/main/manager-web"

if [ -d "$WEB_DIR" ]; then
    cd "$WEB_DIR"
    
    # 检查 Node.js 和 npm
    if ! check_command node; then
        log_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    if ! check_command npm; then
        log_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    
    log_info "Node.js 版本: $(node --version)"
    log_info "npm 版本: $(npm --version)"
    
    if [ -f "package.json" ]; then
        log_info "安装 Web 前端依赖..."
        echo "Web 前端依赖安装开始 - $(date)" >> "$LOG_FILE"
        
        # 设置 npm 镜像源（国内用户）
        npm config set registry https://registry.npmmirror.com >> "$LOG_FILE" 2>&1 || true
        
        # 安装依赖
        npm install >> "$LOG_FILE" 2>&1
        
        log_success "Web 前端依赖安装完成"
        echo "Web 前端依赖安装完成 - $(date)" >> "$LOG_FILE"
    else
        log_warn "未找到 package.json"
    fi
else
    log_warn "manager-web 目录不存在，跳过 Web 前端依赖安装"
fi

# 4. 检查并安装移动端依赖 (manager-mobile)
log_info "========== 安装移动端依赖 (manager-mobile) =========="
MOBILE_DIR="$PROJECT_ROOT/main/manager-mobile"

if [ -d "$MOBILE_DIR" ]; then
    cd "$MOBILE_DIR"
    
    # 优先使用 pnpm，如果没有则使用 npm
    if check_command pnpm; then
        log_info "使用 pnpm 安装移动端依赖"
        log_info "pnpm 版本: $(pnpm --version)"
        
        if [ -f "package.json" ]; then
            log_info "安装移动端依赖..."
            echo "移动端依赖安装开始 (pnpm) - $(date)" >> "$LOG_FILE"
            
            # 设置 pnpm 镜像源（国内用户）
            pnpm config set registry https://registry.npmmirror.com >> "$LOG_FILE" 2>&1 || true
            
            # 安装依赖
            pnpm install >> "$LOG_FILE" 2>&1
            
            log_success "移动端依赖安装完成 (pnpm)"
            echo "移动端依赖安装完成 (pnpm) - $(date)" >> "$LOG_FILE"
        else
            log_warn "未找到 package.json"
        fi
    elif check_command npm; then
        log_info "pnpm 未安装，使用 npm 安装移动端依赖"
        log_warn "建议安装 pnpm 以获得更好的性能: npm install -g pnpm"
        
        if [ -f "package.json" ]; then
            log_info "安装移动端依赖..."
            echo "移动端依赖安装开始 (npm) - $(date)" >> "$LOG_FILE"
            
            # 设置 npm 镜像源（国内用户）
            npm config set registry https://registry.npmmirror.com >> "$LOG_FILE" 2>&1 || true
            
            # 安装依赖
            npm install >> "$LOG_FILE" 2>&1
            
            log_success "移动端依赖安装完成 (npm)"
            echo "移动端依赖安装完成 (npm) - $(date)" >> "$LOG_FILE"
        else
            log_warn "未找到 package.json"
        fi
    else
        log_error "npm 和 pnpm 都未安装，无法安装移动端依赖"
    fi
else
    log_warn "manager-mobile 目录不存在，跳过移动端依赖安装"
fi

# 5. 创建必要的目录
log_info "========== 创建必要目录 =========="
cd "$PROJECT_ROOT"

# 创建 Python 服务所需目录
PYTHON_TMP_DIR="$PROJECT_ROOT/main/xiaozhi-server/tmp"
PYTHON_DATA_DIR="$PROJECT_ROOT/main/xiaozhi-server/data"

if [ ! -d "$PYTHON_TMP_DIR" ]; then
    mkdir -p "$PYTHON_TMP_DIR"
    log_success "创建目录: $PYTHON_TMP_DIR"
fi

if [ ! -d "$PYTHON_DATA_DIR" ]; then
    mkdir -p "$PYTHON_DATA_DIR"
    log_success "创建目录: $PYTHON_DATA_DIR"
    
    # 创建配置文件模板
    cat > "$PYTHON_DATA_DIR/.config.yaml" << EOF
# 本地配置覆盖文件
# 在这里添加你的本地配置，会覆盖 config.yaml 中的默认配置
# 示例:
# selected_module:
#   LLM: ChatGLMLLM
#   TTS: EdgeTTS
# 
# LLM:
#   ChatGLMLLM:
#     api_key: 你的API密钥
EOF
    log_success "创建配置文件模板: $PYTHON_DATA_DIR/.config.yaml"
fi

# 6. 生成依赖总结
log_info "========== 生成依赖安装总结 =========="

echo "" >> "$LOG_FILE"
echo "依赖安装总结 - $(date)" >> "$LOG_FILE"
echo "=====================" >> "$LOG_FILE"

# Python 依赖总结
if [ -f "$PROJECT_ROOT/main/xiaozhi-server/requirements.txt" ]; then
    echo "Python 依赖 (requirements.txt):" >> "$LOG_FILE"
    cat "$PROJECT_ROOT/main/xiaozhi-server/requirements.txt" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
fi

# Java 依赖总结
if [ -f "$PROJECT_ROOT/main/manager-api/pom.xml" ]; then
    echo "Java 依赖版本:" >> "$LOG_FILE"
    cd "$PROJECT_ROOT/main/manager-api"
    if check_command mvn; then
        mvn dependency:list -DoutputFile=dependencies.txt >> "$LOG_FILE" 2>&1 || true
    fi
    echo "" >> "$LOG_FILE"
fi

# Node.js 依赖总结
for dir in "main/manager-web" "main/manager-mobile"; do
    if [ -f "$PROJECT_ROOT/$dir/package.json" ]; then
        echo "$dir 依赖 (package.json):" >> "$LOG_FILE"
        cd "$PROJECT_ROOT/$dir"
        if check_command node; then
            node -e "const pkg=require('./package.json'); console.log('dependencies:', Object.keys(pkg.dependencies || {}).length); console.log('devDependencies:', Object.keys(pkg.devDependencies || {}).length);" >> "$LOG_FILE" 2>&1 || true
        fi
        echo "" >> "$LOG_FILE"
    fi
done

cd "$PROJECT_ROOT"

log_success "========== 所有依赖安装完成! =========="
log_info "安装日志保存在: $LOG_FILE"
log_info "请查看日志文件了解详细的安装过程"

# 显示下一步操作建议
echo ""
log_info "下一步操作建议:"
log_info "1. Python 服务: cd main/xiaozhi-server && python app.py"
log_info "2. Java API: cd main/manager-api && mvn spring-boot:run"
log_info "3. Web 前端: cd main/manager-web && npm run serve"
log_info "4. 移动端: cd main/manager-mobile && pnpm run dev:h5"
log_info "5. 配置文件: 编辑 main/xiaozhi-server/data/.config.yaml"

echo "依赖安装脚本执行完成 - $(date)" >> "$LOG_FILE"