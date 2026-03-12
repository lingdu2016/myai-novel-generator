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
        from src.config.paths import ensure_dirs, get_projects_dir, get_config_dir
        logger.info("Initializing data directories in /data...")
        ensure_dirs()

        # 2. 初始化 Supabase 客户端并从云端恢复数据
        logger.info("Initializing Supabase cloud sync...")
        from src.config.supabase_client import (
            get_supabase_client,
            restore_projects_from_cloud,
            restore_config_from_cloud,
            get_sync_status
        )

        # 尝试初始化 Supabase 客户端
        supabase = get_supabase_client()
        if supabase:
            # 从云端恢复项目数据
            projects_dir = get_projects_dir()
            restored_count = restore_projects_from_cloud(projects_dir)
            logger.info(f"Restored {restored_count} projects from cloud")

            # 从云端恢复配置
            config_file = get_config_dir() / "user_config.json"
            if restore_config_from_cloud(config_file):
                logger.info("Configuration restored from cloud")

            # 打印同步状态
            sync_status = get_sync_status()
            logger.info(f"Cloud sync enabled: {sync_status.get('enabled', False)}")
            logger.info(f"Cloud projects: {sync_status.get('cloud_projects_count', 0)}")
        else:
            logger.info("Supabase not configured, running in local-only mode")

        # 3. 从环境变量加载 API 密钥到配置文件
        from src.config.secrets import load_secrets_to_config
        logger.info("Loading API keys from Hugging Face Secrets...")
        load_secrets_to_config()

        # 4. 注册退出时的 API 日志摘要
        import atexit
        def on_exit():
            try:
                from src.utils.api_logger import get_api_logger
                get_api_logger().summary()
            except:
                pass
        atexit.register(on_exit)

        # 5. 导入并启动应用
        from src.ui.app import main as run_app
        run_app()

    except Exception as e:
        logger.error(f"Failed to start on HF Spaces: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
