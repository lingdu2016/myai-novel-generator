"""
UI层 - Gradio Web界面

这个模块包含完整的Web用户界面，集成所有系统功能。

使用示例：
    from src.ui.app import main
    main()

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

from .app import create_main_ui, create_api_config_ui, create_prompt_editor_ui, main, app_state

__all__ = [
    "create_main_ui",
    "create_api_config_ui",
    "create_prompt_editor_ui",
    "main",
    "app_state",
]
