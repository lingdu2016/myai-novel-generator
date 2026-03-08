#!/usr/bin/env python3
"""
环境检查脚本

检查 Python 版本和依赖兼容性

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
"""

import sys
import importlib
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

# ANSI 颜色代码
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

# 项目所需的核心依赖
REQUIRED_DEPENDENCIES = {
    "gradio": ">=4.44.0,<5.0.0",
    "openai": ">=1.54.0,<2.0.0",
    "httpx": ">=0.24.0,<0.28.0",
    "aiohttp": ">=3.8.0,<3.12.0",
    "pandas": ">=1.5.0,<3.0.0",
    "numpy": ">=1.23.0,<2.2.0",
    "pillow": ">=9.5.0,<12.0.0",
    "jinja2": ">=3.1.0,<4.0.0",
    "pydantic": ">=2.0.0,<3.0.0",
    "fastapi": ">=0.100.0,<0.120.0",
    "uvicorn": ">=0.23.0,<0.33.0",
    "python-docx": ">=1.1.2,<2.0.0",
    "huggingface_hub": ">=0.19.0,<0.25.0",
    "gradio_client": ">=0.16.0,<1.1.0",
}

# 可选依赖
OPTIONAL_DEPENDENCIES = {
    "pytest": ">=8.0.0,<9.0.0",
    "ruff": ">=0.1.0",
    "mypy": ">=1.0.0",
    "ipython": ">=8.12.0",
}

def print_header(text: str) -> None:
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_success(text: str) -> None:
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text: str) -> None:
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str) -> None:
    """打印错误信息"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str) -> None:
    """打印信息"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def check_python_version() -> Tuple[bool, str]:
    """检查 Python 版本"""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    # 支持 3.9 - 3.14
    if version.major == 3 and 9 <= version.minor <= 14:
        if version.minor == 11:
            return True, f"Python {version_str} (推荐版本)"
        elif version.minor >= 13:
            return True, f"Python {version_str} (实验性支持)"
        else:
            return True, f"Python {version_str}"
    else:
        return False, f"Python {version_str} (需要 3.9-3.14)"

def get_package_version(package_name: str) -> str:
    """获取包版本"""
    try:
        if package_name == "python-docx":
            import docx
            return docx.__version__
        elif package_name == "gradio_client":
            import gradio_client
            return getattr(gradio_client, "__version__", "unknown")
        else:
            module = importlib.import_module(package_name)
            return getattr(module, "__version__", "unknown")
    except (ImportError, AttributeError):
        return None

def check_dependencies() -> Dict[str, Tuple[bool, str]]:
    """检查依赖"""
    results = {}

    print(f"{'依赖包':<25} {'需要':<20} {'状态':<15} {'实际版本'}")
    print("-" * 80)

    for name, constraint in REQUIRED_DEPENDENCIES.items():
        version = get_package_version(name)

        if version is None:
            results[name] = (False, "未安装")
            print(f"{name:<25} {constraint:<20} {Colors.RED}{'未安装':<15}{Colors.END} -")
        else:
            results[name] = (True, version)
            print(f"{name:<25} {constraint:<20} {Colors.GREEN}{'已安装':<15}{Colors.END} {version}")

    return results

def check_optional_dependencies() -> None:
    """检查可选依赖"""
    print(f"\n{Colors.BOLD}可选依赖:{Colors.END}\n")
    print(f"{'依赖包':<25} {'需要':<20} {'状态':<15} {'实际版本'}")
    print("-" * 80)

    for name, constraint in OPTIONAL_DEPENDENCIES.items():
        version = get_package_version(name)

        if version is None:
            print(f"{name:<25} {constraint:<20} {Colors.YELLOW}{'未安装':<15}{Colors.END} -")
        else:
            print(f"{name:<25} {constraint:<20} {Colors.GREEN}{'已安装':<15}{Colors.END} {version}")

def check_platform_info() -> None:
    """检查平台信息"""
    print(f"\n{Colors.BOLD}平台信息:{Colors.END}\n")
    print(f"  操作系统: {sys.platform}")
    print(f"  架构: {sys.machine}")
    print(f"  可执行文件: {sys.executable}")

def main():
    """主函数"""
    print_header("AI Novel Generator 4.0 - 环境检查")

    # 检查 Python 版本
    python_ok, python_msg = check_python_version()
    if python_ok:
        print_success(python_msg)
    else:
        print_error(python_msg)
        print(f"\n建议: 请安装 Python 3.11 (推荐) 或 3.9-3.12")
        sys.exit(1)

    # 检查平台信息
    check_platform_info()

    # 检查核心依赖
    print(f"\n{Colors.BOLD}核心依赖检查:{Colors.END}\n")
    dep_results = check_dependencies()

    missing = [name for name, (ok, _) in dep_results.items() if not ok]

    # 检查可选依赖
    check_optional_dependencies()

    # 总结
    print_header("检查总结")

    if not missing:
        print_success("所有核心依赖已安装!")
        print(f"\n运行应用: {Colors.BOLD}python run.py{Colors.END}")
    else:
        print_error(f"缺少 {len(missing)} 个核心依赖")
        print(f"\n请运行以下命令安装依赖:")
        print(f"  {Colors.BOLD}pip install -r requirements.txt{Colors.END}")
        print(f"\n缺少的包: {', '.join(missing)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
