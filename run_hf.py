#!/usr/bin/env python3
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Hugging Face Spaces 启动主函数"""
    try:
        logger.info("=" * 60)
        logger.info("AI Novel Generator - Hugging Face Spaces Edition")
        logger.info("=" * 60)

        # 1. 初始化路径并确保 /data 目录结构
        from src.config.paths import ensure_dirs
        logger.info("Initializing data directories in /data...")
        ensure_dirs()
        
        # 2. 从环境变量加载 API 密钥到配置文件
        from src.config.secrets import load_secrets_to_config
        logger.info("Loading API keys from Hugging Face Secrets...")
        load_secrets_to_config()
        
        # 3. 注册退出时的 API 日志摘要
        import atexit
        def on_exit():
            try:
                from src.utils.api_logger import get_api_logger
                get_api_logger().summary()
            except:
                pass
        atexit.register(on_exit)

        # 4. 导入并启动应用
        from src.ui.app import main as run_app
        run_app()

    except Exception as e:
        logger.error(f"Failed to start on HF Spaces: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
