"""
AI小说生成器 4.0 - PyInstaller打包脚本

使用方法：
    python build_exe.py

输出：
    dist/AI小说生成器4.0.exe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.absolute()

# 打包配置
APP_NAME = "AI小说生成器4.0"
MAIN_SCRIPT = "run.py"
ICON_FILE = None  # 如果有图标文件，填写路径

# 需要包含的数据文件
DATA_FILES = [
    ("config", "config"),
    ("templates", "templates"),
    ("src", "src"),
]

# 需要包含的隐藏导入
HIDDEN_IMPORTS = [
    # Gradio相关
    "gradio",
    "gradio.themes",
    "gradio.themes.base",
    "gradio.themes.utils",
    "gradio.components",
    "gradio.layouts",
    "gradio.blocks",
    "gradio.events",
    "gradio.routes",
    "gradio.utils",
    "gradio.data_classes",
    "gradio.exceptions",
    "gradio.processing_utils",
    "gradio.state_holder",
    "gradio.context",
    "gradio.external_utils",
    "gradio.networking",
    "gradio.strings",
    "gradio.templating",
    "gradio.cli",
    "gradio.analytics",
    "gradio.documentation",
    "gradio.internals",
    
    # API相关
    "openai",
    "openai.types",
    "openai.resources",
    "anthropic",
    "google.generativeai",
    
    # 工具库
    "tiktoken",
    "yaml",
    "jinja2",
    "markdown",
    "PIL",
    "PIL.Image",
    "numpy",
    "pandas",
    "requests",
    "aiohttp",
    "websockets",
    
    # Web框架
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "fastapi",
    "fastapi.routing",
    "fastapi.middleware",
    "fastapi.staticfiles",
    "fastapi.templating",
    "fastapi.responses",
    "fastapi.requests",
    "starlette",
    "starlette.routing",
    "starlette.middleware",
    "starlette.staticfiles",
    "starlette.templating",
    "starlette.responses",
    "starlette.requests",
    "starlette.websockets",
    "starlette.exceptions",
    "starlette.status",
    "starlette.datastructures",
    "starlette.types",
    "starlette.concurrency",
    "starlette.config",
    "starlette.convertors",
    "starlette.formparsers",
    "starlette.testclient",
    
    # HTTP相关
    "python-multipart",
    "httpx",
    "httpcore",
    "httpcore._backends",
    "httpcore._backends.auto",
    "httpcore._sync",
    "httpcore._sync.connection",
    "httpcore._sync.http11",
    "httpcore._sync.http2",
    "h11",
    "anyio",
    "anyio._backends",
    "anyio._backends._asyncio",
    "sniffio",
    
    # 其他
    "pydantic",
    "pydantic.fields",
    "pydantic.main",
    "pydantic.types",
    "pydantic.validators",
    "pydantic.error_wrappers",
    "pydantic.errors",
    "pydantic.parse",
    "pydantic.schema",
    "pydantic.json",
    "pydantic.env_settings",
    "pydantic.tools",
    "pydantic.version",
    "typing_extensions",
    "annotated_types",
    "email_validator",
    "watchfiles",
    "watchfiles.main",
]


def clean_build():
    """清理构建目录"""
    print("[CLEAN] 清理构建目录...")
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        dir_path = ROOT_DIR / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  [OK] 删除 {dir_name}/")

    # 删除spec文件
    for spec_file in ROOT_DIR.glob("*.spec"):
        spec_file.unlink()
        print(f"  [OK] 删除 {spec_file.name}")


def create_spec_file():
    """创建spec文件"""
    print("\n[CREATE] 创建spec文件...")

    # 构建数据文件列表
    datas = []
    for src, dst in DATA_FILES:
        src_path = ROOT_DIR / src
        if src_path.exists():
            datas.append(f'("{src}", "{dst}")')

    datas_str = ",\n    ".join(datas)

    # 构建隐藏导入列表
    hiddenimports = []
    for module in HIDDEN_IMPORTS:
        hiddenimports.append(f'"{module}"')

    hiddenimports_str = ",\n    ".join(hiddenimports)

    # spec文件内容
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas=[
        {datas_str}
    ],
    hiddenimports=[
        {hiddenimports_str}
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={f'r"{ICON_FILE}"' if ICON_FILE else None},
)
"""

    spec_file = ROOT_DIR / f"{APP_NAME}.spec"
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print(f"  [OK] 创建 {spec_file.name}")
    return spec_file


def build_exe(spec_file):
    """执行打包"""
    print("\n[BUILD] 开始打包...")
    print("  这可能需要几分钟时间，请耐心等待...\n")

    try:
        # 使用pyinstaller打包
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", str(spec_file)],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("\n[OK] 打包成功！")
            return True
        else:
            print("\n[ERROR] 打包失败！")
            print("\n错误信息：")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"\n[ERROR] 打包过程出错: {e}")
        return False


def create_runtime_files():
    """创建运行时需要的目录和文件"""
    print("\n[DIR] 创建运行时文件...")

    dist_dir = ROOT_DIR / "dist"
    if not dist_dir.exists():
        return

    # 在dist目录创建必要的目录
    dirs_to_create = ["projects", "logs", "logs/api_samples", "cache", "data"]
    for dir_name in dirs_to_create:
        dir_path = dist_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        # 创建.gitkeep文件
        (dir_path / ".gitkeep").touch()
        print(f"  [OK] 创建 {dir_name}/")


def print_success_info():
    """打印成功信息"""
    print("\n" + "=" * 60)
    print("[SUCCESS] 打包完成！")
    print("=" * 60)
    print(f"\n可执行文件位置：")
    print(f"  {ROOT_DIR / 'dist' / APP_NAME}.exe")
    print(f"\n使用方法：")
    print(f"  1. 双击运行 {APP_NAME}.exe")
    print(f"  2. 等待服务器启动")
    print(f"  3. 浏览器访问 http://127.0.0.1:7860")
    print(f"\n注意事项：")
    print(f"  - 首次启动可能需要较长时间")
    print(f"  - 请确保防火墙允许程序运行")
    print(f"  - 日志文件保存在 logs/ 目录")
    print(f"  - 项目文件保存在 projects/ 目录")
    print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print(f"{APP_NAME} - 打包工具")
    print("=" * 60)

    # 检查Python版本
    if sys.version_info < (3, 10):
        print("[ERROR] 错误：需要Python 3.10或更高版本")
        sys.exit(1)

    print(f"Python版本: {sys.version}")
    print(f"工作目录: {ROOT_DIR}")

    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("\n[ERROR] 错误：未安装PyInstaller")
        print("请运行: pip install pyinstaller")
        sys.exit(1)

    # 执行打包流程
    clean_build()
    spec_file = create_spec_file()

    if build_exe(spec_file):
        create_runtime_files()
        print_success_info()
    else:
        print("\n[ERROR] 打包失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
