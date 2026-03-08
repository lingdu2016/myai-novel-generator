"""
AI Novel Generator 4.0

重构版本，具有以下核心功能：
- 智能连贯性系统（角色跟踪、剧情管理、世界观数据库）
- 灵活的提示词系统（18+预设模板、变量替换）
- 统一API客户端（22+提供商支持）
- 简化的用户界面

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

__version__ = "4.0.0"
__author__ = "幻城"

# 延迟导入，避免在__init__.py时加载所有依赖
def __getattr__(name):
    """延迟导入模块"""
    if name == "UnifiedAPIClient":
        from .api import UnifiedAPIClient
        return UnifiedAPIClient
    elif name == "create_api_client":
        from .api import create_api_client
        return create_api_client
    elif name == "CharacterTracker":
        from .core.coherence import CharacterTracker
        return CharacterTracker
    elif name == "PlotManager":
        from .core.coherence import PlotManager
        return PlotManager
    elif name == "WorldDatabase":
        from .core.coherence import WorldDatabase
        return WorldDatabase
    elif name == "ContextBuilder":
        from .core.coherence import ContextBuilder
        return ContextBuilder
    elif name == "CoherenceValidator":
        from .core.coherence import CoherenceValidator
        return CoherenceValidator
    elif name == "PromptManager":
        from .core.prompts import PromptManager
        return PromptManager
    elif name == "ProviderFactory":
        from .config.providers import ProviderFactory
        return ProviderFactory
    elif name == "PRESET_PROVIDERS":
        from .config.providers import PRESET_PROVIDERS
        return PRESET_PROVIDERS
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # API
    "UnifiedAPIClient",
    "create_api_client",

    # Coherence
    "CharacterTracker",
    "PlotManager",
    "WorldDatabase",
    "ContextBuilder",
    "CoherenceValidator",

    # Prompts
    "PromptManager",

    # Config
    "ProviderFactory",
    "PRESET_PROVIDERS",
]
