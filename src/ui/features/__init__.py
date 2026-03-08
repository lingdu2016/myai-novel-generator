"""
UI功能模块包
包含各种UI功能：润色、重写、大纲生成、缓存管理、参数配置、批量生成、自动生成等

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
"""

from .polish import create_polish_ui
from .rewrite import create_rewrite_ui
from .outline import create_outline_ui
from .cache_manager import create_cache_manager_ui
from .params_config import create_params_config_ui
from .batch_generation import create_batch_generation_ui
from .auto_generation import create_auto_generation_ui, AutoNovelGenerator

__all__ = [
    'create_polish_ui',
    'create_rewrite_ui',
    'create_outline_ui',
    'create_cache_manager_ui',
    'create_params_config_ui',
    'create_batch_generation_ui',
    'create_auto_generation_ui',
    'AutoNovelGenerator',
]
