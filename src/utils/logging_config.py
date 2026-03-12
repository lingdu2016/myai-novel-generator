"""
统一日志配置模块

提供完整的日志系统配置，包括：
- 分级日志文件（INFO/DEBUG/ERROR）
- API采样日志
- 性能统计日志
- 格式化输出

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
"""

import logging
import sys
from pathlib import Path
from ..config.paths import get_logs_dir
from datetime import datetime
from typing import Optional
import atexit


class LogConfig:
    """日志配置类"""

    # 日志目录
    LOG_DIR = get_logs_dir()
    # LOG_DIR.mkdir(exist_ok=True)

    # 日志标签前缀
    LOG_TAGS = {
        "app": "[应用]",
        "api": "[API]",
        "coherence": "[连贯性]",
        "character": "[角色跟踪]",
        "plot": "[剧情管理]",
        "world": "[世界观]",
        "context": "[上下文]",
        "prompt": "[提示词]",
        "generation": "[自动生成]",
        "polish": "[润色功能]",
        "rewrite": "[重写续写]",
        "outline": "[大纲生成]",
        "project": "[项目管理]",
        "export": "[导出功能]",
        "batch": "[批量生成]",
        "provider": "[提供商]",
        "validation": "[验证]",
    }

    @classmethod
    def setup_logging(cls, log_level: str = "INFO") -> logging.Logger:
        """
        配置完整的日志系统

        Args:
            log_level: 日志级别 (DEBUG/INFO/WARNING/ERROR)

        Returns:
            配置好的根日志记录器
        """
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器（彩色输出）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)

        # 文件处理器 - 主日志（INFO级别）
        main_log_file = cls.LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(main_log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # 文件处理器 - 调试日志（DEBUG级别）
        debug_log_file = cls.LOG_DIR / f"debug_{datetime.now().strftime('%Y%m%d')}.log"
        debug_handler = logging.FileHandler(debug_log_file, encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)

        # 文件处理器 - 错误日志（ERROR级别）
        error_log_file = cls.LOG_DIR / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # 最低级别，让handler过滤
        root_logger.handlers.clear()  # 清除现有handlers
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(debug_handler)
        root_logger.addHandler(error_handler)

        # 关闭第三方库的DEBUG日志
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('gradio').setLevel(logging.INFO)
        logging.getLogger('asyncio').setLevel(logging.WARNING)

        # 打印初始化信息
        logger = logging.getLogger(__name__)
        logger.info("=" * 70)
        logger.info("AI Novel Generator 4.0 - 日志系统初始化完成")
        logger.info(f"日志目录: {cls.LOG_DIR.absolute()}")
        logger.info(f"主日志文件: {main_log_file}")
        logger.info(f"调试日志文件: {debug_log_file}")
        logger.info(f"错误日志文件: {error_log_file}")
        logger.info(f"日志级别: {log_level}")
        logger.info("=" * 70)

        # 注册退出时的日志摘要
        atexit.register(cls._log_summary)

        return logger

    @classmethod
    def _log_summary(cls):
        """程序退出时输出日志摘要"""
        logger = logging.getLogger(__name__)
        logger.info("=" * 70)
        logger.info("程序即将退出 - 日志系统关闭")
        logger.info(f"日志文件保存在: {cls.LOG_DIR.absolute()}")
        logger.info("=" * 70)

    @classmethod
    def get_logger(cls, name: str, tag: Optional[str] = None) -> logging.Logger:
        """
        获取带有标签的日志记录器

        Args:
            name: 日志记录器名称
            tag: 日志标签（会自动添加前缀）

        Returns:
            配置好的日志记录器
        """
        logger = logging.getLogger(name)

        if tag:
            # 使用LoggerAdapter添加标签前缀
            logger = logging.LoggerAdapter(logger, {"tag": cls.LOG_TAGS.get(tag, f"[{tag}]")})

        return logger

    @classmethod
    def log_with_tag(cls, tag: str, level: str, message: str):
        """
        使用标签快速记录日志

        Args:
            tag: 标签名称
            level: 日志级别 (info/debug/warning/error)
            message: 日志消息
        """
        tag_prefix = cls.LOG_TAGS.get(tag, f"[{tag}]")
        logger = logging.getLogger(tag)

        log_method = getattr(logger, level.lower(), logger.info)
        log_method(f"{tag_prefix} {message}")


# 便捷函数
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """设置日志系统"""
    return LogConfig.setup_logging(log_level)


def get_logger(name: str, tag: Optional[str] = None) -> logging.Logger:
    """获取日志记录器"""
    return LogConfig.get_logger(name, tag)


# 初始化日志系统（自动执行）
_root_logger = None


def init_logging():
    """初始化日志系统（单例）"""
    global _root_logger
    if _root_logger is None:
        _root_logger = setup_logging()
    return _root_logger
