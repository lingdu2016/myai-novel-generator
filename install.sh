#!/bin/bash
# ============================================================
# AI Novel Generator 4.0 - 依赖安装脚本 (Linux/macOS)
# 版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "\n${BOLD}${BLUE}========================================${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BOLD}${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 检查 Python 版本
check_python_version() {
    print_header "检查 Python 版本"

    PYTHON_CMD=""

    # 查找 Python 命令
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
    else
        print_error "未找到 Python"
        print_info "请安装 Python 3.9 或更高版本"
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

    print_info "检测到 Python 版本: $PYTHON_VERSION"

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        print_error "需要 Python 3.9 或更高版本"
        print_info "当前版本: $PYTHON_VERSION"
        exit 1
    fi

    print_success "Python 版本符合要求"

    # 推荐 Python 3.11
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -eq 11 ]; then
        print_success "使用推荐的 Python 3.11 版本"
    fi
}

# 检查虚拟环境
check_venv() {
    print_header "检查虚拟环境"

    if [ -n "$VIRTUAL_ENV" ]; then
        print_success "虚拟环境已激活: $VIRTUAL_ENV"
    else
        print_warning "未检测到虚拟环境"

        # 创建虚拟环境选项
        if [ -d "venv" ]; then
            print_info "发现本地 venv 目录"
            read -p "是否激活本地虚拟环境? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if [ -f "venv/bin/activate" ]; then
                    source venv/bin/activate
                    print_success "虚拟环境已激活"
                    return
                fi
            fi
        fi

        read -p "是否创建新的虚拟环境? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "创建虚拟环境..."
            $PYTHON_CMD -m venv venv
            print_success "虚拟环境已创建: venv/"

            print_info "请先激活虚拟环境，然后重新运行此脚本:"
            echo ""
            echo "  source venv/bin/activate  # Linux/macOS"
            echo "  ./install.sh"
            echo ""
            exit 0
        fi
    fi
}

# 选择安装类型
select_install_type() {
    print_header "选择安装类型"

    echo "请选择安装类型:"
    echo "  1) 生产环境 (最小依赖)"
    echo "  2) 开发环境 (包含开发工具)"
    echo "  3) 重新安装所有依赖"
    read -p "请输入选择 [1/3] (默认: 1): " choice

    case $choice in
        2)
            INSTALL_TYPE="dev"
            print_info "将安装开发依赖"
            ;;
        3)
            INSTALL_TYPE="reinstall"
            print_info "将重新安装所有依赖"
            ;;
        *)
            INSTALL_TYPE="prod"
            print_info "将安装生产依赖"
            ;;
    esac
}

# 安装依赖
install_dependencies() {
    print_header "安装依赖"

    if [ "$INSTALL_TYPE" = "dev" ]; then
        print_info "安装开发依赖..."
        pip install -r requirements-dev.txt
    elif [ "$INSTALL_TYPE" = "reinstall" ]; then
        print_info "重新安装所有依赖..."
        pip install --force-reinstall -r requirements.txt
    else
        print_info "安装生产依赖..."
        pip install -r requirements.txt
    fi

    if [ $? -eq 0 ]; then
        print_success "依赖安装完成"
    else
        print_error "依赖安装失败"
        exit 1
    fi
}

# 运行环境检查
run_check() {
    print_header "环境检查"

    if [ -f "scripts/check_env.py" ]; then
        python scripts/check_env.py
    else
        print_warning "环境检查脚本不存在，跳过"
    fi
}

# 显示完成信息
show_completion() {
    print_header "安装完成"

    echo "运行应用:"
    echo "  python run.py"
    echo ""
    echo "或者使用环境检查:"
    echo "  python scripts/check_env.py"
    echo ""
}

# 主流程
main() {
    print_header "AI Novel Generator 4.0 - 依赖安装"

    check_python_version
    check_venv
    select_install_type
    install_dependencies
    run_check
    show_completion
}

# 运行主流程
main
