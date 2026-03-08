"""
提示词系统 - 去AI化版本
让AI写出真正像人写的文字

这个模块提供了完整的提示词管理功能，包括：
- 去AI化的系统提示词
- AI禁忌词列表
- 好示例/坏示例库
- 18+预设风格模板
- 风格约束模板

使用示例：
from src.core.prompts import PromptManager, get_banned_words, get_writing_examples

# 获取禁忌词列表
banned_words = get_banned_words()

# 获取写作示例
examples = get_writing_examples()

# 获取系统提示词
from src.core.prompts import get_system_prompt
prompt = get_system_prompt("novel_writer", genre="玄幻")

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

from .manager import PromptManager, get_prompt_manager
from .variables import (
    PromptVariableManager,
    create_generation_prompt,
    create_rewrite_prompt
)
from .templates import (
    PRESET_TEMPLATES,
    get_preset_template,
    list_preset_templates,
    get_style_constraints,
    get_writing_examples as get_templates_writing_examples,
    build_chapter_prompt,
    STYLE_CONSTRAINTS,
    WRITING_EXAMPLES,
)
from .system_prompts import (
    SYSTEM_PROMPTS,
    GENRE_SYSTEM_PROMPTS,
    TECHNIQUE_GUIDES,
    get_system_prompt,
    get_technique_guide,
    get_banned_words,
    get_writing_examples,
    AI_BANNED_WORDS,
    WRITING_EXAMPLES_GOOD,
    WRITING_EXAMPLES_BAD,
)
from .advanced_templates import (
    ADVANCED_PRESET_TEMPLATES,
    get_advanced_template,
    list_advanced_templates,
    get_technique_example,
    COMMON_TECHNIQUES
)

__all__ = [
    # Manager
    "PromptManager",
    "get_prompt_manager",

    # Variables
    "PromptVariableManager",
    "create_generation_prompt",
    "create_rewrite_prompt",

    # Templates
    "PRESET_TEMPLATES",
    "get_preset_template",
    "list_preset_templates",
    "get_style_constraints",
    "build_chapter_prompt",
    "STYLE_CONSTRAINTS",
    "WRITING_EXAMPLES",

    # System Prompts
    "SYSTEM_PROMPTS",
    "GENRE_SYSTEM_PROMPTS",
    "TECHNIQUE_GUIDES",
    "get_system_prompt",
    "get_technique_guide",

    # Anti-AI Features
    "AI_BANNED_WORDS",
    "WRITING_EXAMPLES_GOOD",
    "WRITING_EXAMPLES_BAD",
    "get_banned_words",
    "get_writing_examples",

    # Advanced Templates
    "ADVANCED_PRESET_TEMPLATES",
    "get_advanced_template",
    "list_advanced_templates",
    "get_technique_example",
    "COMMON_TECHNIQUES",
]