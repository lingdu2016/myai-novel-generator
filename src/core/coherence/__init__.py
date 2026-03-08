"""
连贯性系统 - 确保小说章节间的连贯性和一致性

这个模块提供了完整的连贯性管理系统，包括：
- 角色状态跟踪
- 剧情线管理
- 世界观数据库
- 智能上下文生成
- 连贯性验证

使用示例：
    from src.core.coherence import (
        CharacterTracker,
        PlotManager,
        WorldDatabase,
        ContextBuilder,
        CoherenceValidator
    )

    # 初始化系统
    char_tracker = CharacterTracker(project_id="my_novel")
    plot_manager = PlotManager(project_id="my_novel")
    world_db = WorldDatabase(project_id="my_novel")

    # 构建上下文用于生成
    context = build_context_for_generation(
        current_chapter=5,
        chapter_outline="...",
        chapter_desc="...",
        character_tracker=char_tracker,
        plot_manager=plot_manager,
        world_db=world_db,
        api_client=api_client
    )

    # 验证连贯性
    result = validate_chapter_coherence(
        chapter_content="...",
        chapter_num=5,
        chapter_outline="...",
        character_tracker=char_tracker,
        plot_manager=plot_manager,
        world_db=world_db,
        api_client=api_client
    )

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

from .character_tracker import (
    CharacterTracker,
    CharacterState,
    CharacterEvent,
    analyze_characters_from_chapter
)

from .plot_manager import (
    PlotManager,
    PlotThread,
    PlotEvent,
    PlotStatus,
    PlotType,
    analyze_plot_from_chapter
)

from .world_db import (
    WorldDatabase,
    Location,
    Item,
    WorldRule,
    TimelineEvent,
    extract_world_setting_from_chapter
)

from .context_builder import (
    ContextBuilder,
    build_context_for_generation
)

from .validator import (
    CoherenceValidator,
    ValidationIssue,
    ValidationResult,
    validate_chapter_coherence
)

from .hierarchical_summary import (
    HierarchicalSummaryManager
)

__all__ = [
    # Character Tracker
    "CharacterTracker",
    "CharacterState",
    "CharacterEvent",
    "analyze_characters_from_chapter",

    # Plot Manager
    "PlotManager",
    "PlotThread",
    "PlotEvent",
    "PlotStatus",
    "PlotType",
    "analyze_plot_from_chapter",

    # World Database
    "WorldDatabase",
    "Location",
    "Item",
    "WorldRule",
    "TimelineEvent",
    "extract_world_setting_from_chapter",

    # Context Builder
    "ContextBuilder",
    "build_context_for_generation",

    # Validator
    "CoherenceValidator",
    "ValidationIssue",
    "ValidationResult",
    "validate_chapter_coherence",
    
    # Hierarchical Summary
    "HierarchicalSummaryManager",
]
