@echo off
REM ============================================================
REM AI Novel Generator 4.0 - 依赖安装脚本 (Windows)
REM 版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
REM ============================================================

setlocal enabledelayedexpansion

echo ========================================
echo AI Novel Generator 4.0 - 依赖安装
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [信息] 检测到 Python 版本: %PYTHON_VERSION%
echo.

REM 检查虚拟环境
if defined VIRTUAL_ENV (
    echo [成功] 虚拟环境已激活: %VIRTUAL_ENV%
) else (
    echo [警告] 未检测到虚拟环境

    if exist venv (
        echo [信息] 发现本地 venv 目录
        set /p ACTIVATE="是否激活本地虚拟环境? (y/n): "
        if /i "!ACTIVATE!"=="y" (
            call venv\Scripts\activate.bat
            echo [成功] 虚拟环境已激活
            goto :venv_done
        )
    )

    set /p CREATE="是否创建新的虚拟环境? (y/n): "
    if /i "!CREATE!"=="y" (
        echo [信息] 创建虚拟环境...
        python -m venv venv
        echo [成功] 虚拟环境已创建: venv\
        echo.
        echo 请先激活虚拟环境，然后重新运行此脚本:
        echo   venv\Scripts\activate
        echo   install.bat
        echo.
        pause
        exit /b 0
    )
)

:venv_done
echo.

REM 选择安装类型
echo 请选择安装类型:
echo   1) 生产环境 (最小依赖)
echo   2) 开发环境 (包含开发工具)
echo   3) 重新安装所有依赖
set /p CHOICE="请输入选择 [1/3] (默认: 1): "

if "%CHOICE%"=="2" (
    set INSTALL_TYPE=dev
    echo [信息] 将安装开发依赖
) else if "%CHOICE%"=="3" (
    set INSTALL_TYPE=reinstall
    echo [信息] 将重新安装所有依赖
) else (
    set INSTALL_TYPE=prod
    echo [信息] 将安装生产依赖
)

echo.
echo ========================================
echo 安装依赖
echo ========================================
echo.

if "%INSTALL_TYPE%"=="dev" (
    pip install -r requirements-dev.txt
) else if "%INSTALL_TYPE%"=="reinstall" (
    pip install --force-reinstall -r requirements.txt
) else (
    pip install -r requirements.txt
)

if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo [成功] 依赖安装完成
echo.

REM 运行环境检查
if exist scripts\check_env.py (
    echo ========================================
    echo 环境检查
    echo ========================================
    python scripts\check_env.py
)

echo.
echo ========================================
echo 安装完成
echo ========================================
echo.
echo 运行应用:
echo   python run.py
echo.
echo 或者使用环境检查:
echo   python scripts\check_env.py
echo.
pause
