"""
AI小说生成工具 - 核心模块

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

# 连贯性系统
from .coherence import (
    CharacterTracker,
    PlotManager,
    WorldDatabase,
    ContextBuilder,
    CoherenceValidator,
    build_context_for_generation,
    validate_chapter_coherence,
    analyze_characters_from_chapter,
    analyze_plot_from_chapter,
    extract_world_setting_from_chapter,
)

# 提示词系统
from .prompts import PromptManager

# 增强系统（新增）
from .enhanced_context import (
    EnhancedContextBuilder,
    ForeshadowingManager,
    ChapterTransitionGenerator,
    create_enhanced_context_builder,
)

from .style_optimizer import (
    AITasteDetector,
    AITasteCorrector,
    StyleOptimizer,
    detect_and_optimize,
    get_style_score,
)

from .quality_assessor import (
    QualityAssessor,
    QualityDimension,
    QualityScore,
    assess_chapter_quality,
)

from .optimized_generator import (
    OptimizedNovelGenerator,
    create_optimized_generator,
)

__all__ = [
    # 连贯性系统
    "CharacterTracker",
    "PlotManager",
    "WorldDatabase",
    "ContextBuilder",
    "CoherenceValidator",
    "build_context_for_generation",
    "validate_chapter_coherence",
    "analyze_characters_from_chapter",
    "analyze_plot_from_chapter",
    "extract_world_setting_from_chapter",

    # 提示词系统
    "PromptManager",

    # 增强系统
    "EnhancedContextBuilder",
    "ForeshadowingManager",
    "ChapterTransitionGenerator",
    "create_enhanced_context_builder",

    # 风格优化
    "AITasteDetector",
    "AITasteCorrector",
    "StyleOptimizer",
    "detect_and_optimize",
    "get_style_score",

    # 质量评估
    "QualityAssessor",
    "QualityDimension",
    "QualityScore",
    "assess_chapter_quality",

    # 优化生成器
    "OptimizedNovelGenerator",
    "create_optimized_generator",
]
