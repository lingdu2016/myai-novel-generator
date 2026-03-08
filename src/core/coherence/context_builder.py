"""
智能上下文生成器 - AI驱动的上下文构建，确保章节连贯性

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path

from .character_tracker import CharacterTracker
from .plot_manager import PlotManager
from .world_db import WorldDatabase

logger = logging.getLogger(__name__)


class ContextBuilder:
    """
    智能上下文构建器

    功能：
    1. 分析章节大纲，提取关键信息
    2. 从角色、剧情、世界观数据库中选择相关信息
    3. 智能组合生成优化的上下文
    4. 确保上下文长度不超过限制
    """

    def __init__(
        self,
        character_tracker: CharacterTracker,
        plot_manager: PlotManager,
        world_db: WorldDatabase,
        api_client
    ):
        """
        初始化上下文构建器

        Args:
            character_tracker: 角色跟踪器
            plot_manager: 剧情管理器
            world_db: 世界观数据库
            api_client: API客户端（用于AI分析）
        """
        self.character_tracker = character_tracker
        self.plot_manager = plot_manager
        self.world_db = world_db
        self.api_client = api_client

    def build_generation_context(
        self,
        current_chapter: int,
        chapter_outline: str,
        chapter_desc: str,
        max_length: int = 2000
    ) -> str:
        """
        构建生成上下文

        Args:
            current_chapter: 当前章节号
            chapter_outline: 章节大纲
            chapter_desc: 章节描述
            max_length: 最大长度（字符数）

        Returns:
            格式化的上下文文本
        """
        logger.info(f"[上下文构建] 开始为第{current_chapter}章构建上下文，最大长度: {max_length}")

        # 如果是第一章，返回基础设定
        if current_chapter == 1:
            logger.debug(f"[上下文构建] 第一章使用基础设定")
            return self._build_first_chapter_context(chapter_outline, chapter_desc)

        # 使用AI分析章节大纲，提取关键信息
        key_info = self._analyze_chapter_outline(chapter_outline, chapter_desc)

        # 根据关键信息组装上下文
        context_parts = []

        # 1. 前文摘要（最近1-2章的关键内容）
        context_parts.append(self._get_recent_summary(current_chapter))

        # 2. 相关角色信息
        characters = key_info.get("characters", [])
        if characters:
            context_parts.append(self._get_characters_context(characters, current_chapter))

        # 3. 相关剧情线
        plot_threads = key_info.get("plot_threads", [])
        if plot_threads:
            context_parts.append(self._get_plot_context(plot_threads, current_chapter))

        # 4. 相关世界观
        world_topics = key_info.get("world_topics", [])
        if world_topics:
            context_parts.append(self._get_world_context(world_topics))

        # 5. 未解决的伏笔和悬念
        context_parts.append(self._get_unresolved_elements(current_chapter))

        # 组装并截断
        full_context = "\n\n".join([p for p in context_parts if p])

        if len(full_context) > max_length:
            original_len = len(full_context)
            full_context = self._smart_truncate(full_context, max_length)
            logger.debug(f"[上下文构建] 上下文已截断: {original_len} -> {len(full_context)} 字符")

        logger.info(f"[上下文构建] 第{current_chapter}章上下文构建完成，最终长度: {len(full_context)} 字符")
        return full_context

    def _build_first_chapter_context(
        self,
        chapter_outline: str,
        chapter_desc: str
    ) -> str:
        """构建第一章的上下文（主要是设定）"""
        context_parts = [
            "【第一章起始】",
            f"章节大纲：{chapter_outline}",
            f"章节描述：{chapter_desc}",
        ]

        # 添加世界观基础信息
        world_summary = self.world_db.get_world_summary()
        if world_summary:
            context_parts.append(world_summary)

        return "\n\n".join(context_parts)

    def _analyze_chapter_outline(
        self,
        chapter_outline: str,
        chapter_desc: str
    ) -> Dict[str, List[str]]:
        """
        使用AI分析章节大纲，提取关键信息

        Args:
            chapter_outline: 章节大纲
            chapter_desc: 章节描述

        Returns:
            包含characters, plot_threads, world_topics的字典
        """
        logger.debug(f"[上下文构建] 使用AI分析章节大纲")

        prompt = f"""分析以下章节信息，提取本章需要关注的关键要素。

章节大纲：
{chapter_outline}

章节描述：
{chapter_desc}

请以JSON格式返回：
{{
    "characters": ["角色1", "角色2"],  // 本章涉及的主要角色
    "plot_threads": ["剧情线1", "剧情线2"],  // 本章涉及的剧情线（如主线、感情线等）
    "world_topics": ["地点1", "物品1", "规则1"]  // 本章涉及的世界观元素
}}

只返回JSON，不要其他文字。如果某类信息不明确，返回空列表。"""

        try:
            response = self.api_client.generate([
                {"role": "system", "content": "你是一个专业的小说分析助手。"},
                {"role": "user", "content": prompt}
            ], temperature=0.3)

            import json
            result = json.loads(response)
            return result

        except Exception as e:
            logger.error(f"[上下文构建] AI分析章节大纲失败: {e}", exc_info=True)
            return {"characters": [], "plot_threads": [], "world_topics": []}

    def _get_recent_summary(self, current_chapter: int) -> str:
        """
        获取最近章节的摘要

        Args:
            current_chapter: 当前章节号

        Returns:
            最近章节摘要
        """
        # 获取上一章的关键事件
        prev_chapter = current_chapter - 1
        events = self.plot_manager.get_threads_in_chapter(prev_chapter)

        if not events:
            return ""

        summary_parts = [f"【前文回顾（第{prev_chapter}章）】"]

        for thread in events[:3]:  # 最多3条
            # 获取该剧情线在上一章的事件
            recent_events = [
                event for event in thread.key_events
                if event.chapter_num == prev_chapter
            ]
            for event in recent_events[:2]:  # 每条线最多2个事件
                summary_parts.append(f"- {event.description}")

        return "\n".join(summary_parts) if len(summary_parts) > 1 else ""

    def _get_characters_context(
        self,
        characters: List[str],
        current_chapter: int
    ) -> str:
        """
        获取角色上下文

        Args:
            characters: 角色名列表
            current_chapter: 当前章节号

        Returns:
            角色状态摘要
        """
        context_parts = ["【角色状态】"]

        for char_name in characters[:5]:  # 最多5个角色
            summary = self.character_tracker.get_character_summary_for_context(
                char_name,
                current_chapter - 1
            )
            if summary:
                context_parts.append(summary)

        return "\n\n".join(context_parts) if len(context_parts) > 1 else ""

    def _get_plot_context(
        self,
        plot_threads: List[str],
        current_chapter: int
    ) -> str:
        """
        获取剧情线上下文

        Args:
            plot_threads: 剧情线名称列表
            current_chapter: 当前章节号

        Returns:
            剧情线摘要
        """
        # 获取所有活跃的剧情线
        active_threads = self.plot_manager.get_active_threads()

        if not active_threads:
            return ""

        context_parts = ["【剧情进展】"]

        for thread in active_threads[:3]:  # 最多3条主线
            # 获取该剧情线到上一章的最新进展
            events_before_chapter = [
                event for event in thread.key_events
                if event.chapter_num < current_chapter
            ]

            if events_before_chapter:
                last_event = events_before_chapter[-1]
                context_parts.append(
                    f"{thread.name}: {last_event.description}"
                )

                # 添加未解决的伏笔
                foreshadowing = self.plot_manager.get_unresolved_foreshadowing(thread.id)
                if foreshadowing:
                    context_parts.append(f"  未解决伏笔: {foreshadowing[0]}")

                # 添加未解决的悬念
                cliffhangers = self.plot_manager.get_unresolved_cliffhangers(thread.id)
                if cliffhangers:
                    context_parts.append(f"  当前悬念: {cliffhangers[0]}")

        return "\n".join(context_parts) if len(context_parts) > 1 else ""

    def _get_world_context(self, world_topics: List[str]) -> str:
        """
        获取世界观上下文

        Args:
            world_topics: 世界观主题列表

        Returns:
            世界观信息
        """
        context_parts = []

        for topic in world_topics:
            context = self.world_db.get_relevant_context(topic, max_length=200)
            if context:
                context_parts.append(context)

        return "\n\n".join(context_parts) if context_parts else ""

    def _get_unresolved_elements(self, current_chapter: int) -> str:
        """
        获取未解决的伏笔和悬念

        Args:
            current_chapter: 当前章节号

        Returns:
            未解决元素列表
        """
        context_parts = ["【待解决要素】"]

        # 获取所有未解决的伏笔
        all_foreshadowing = self.plot_manager.get_unresolved_foreshadowing()
        if all_foreshadowing:
            context_parts.append(f"未解决伏笔（共{len(all_foreshadowing)}个）:")
            for fs in all_foreshadowing[:3]:  # 最多3个
                context_parts.append(f"  - {fs}")

        # 获取所有未解决的悬念
        all_cliffhangers = self.plot_manager.get_unresolved_cliffhangers()
        if all_cliffhangers:
            context_parts.append(f"\n未解决悬念（共{len(all_cliffhangers)}个）:")
            for ch in all_cliffhangers[:2]:  # 最多2个
                context_parts.append(f"  - {ch}")

        return "\n".join(context_parts) if len(context_parts) > 1 else ""

    def _smart_truncate(self, text: str, max_length: int) -> str:
        """
        智能截断文本

        优先保留：
        1. 完整的段落
        2. 角色信息
        3. 剧情信息

        Args:
            text: 原文本
            max_length: 最大长度

        Returns:
            截断后的文本
        """
        if len(text) <= max_length:
            return text

        # 按段落分割
        paragraphs = text.split("\n\n")

        # 优先保留包含关键词的段落
        priority_keywords = ["【角色状态】", "【剧情进展】", "【前文回顾】"]
        result_paragraphs = []

        # 先添加高优先级段落
        for para in paragraphs:
            if any(keyword in para for keyword in priority_keywords):
                result_paragraphs.append(para)

        # 如果还有空间，添加其他段落
        for para in paragraphs:
            if para not in result_paragraphs:
                if len("\n\n".join(result_paragraphs)) + len(para) < max_length:
                    result_paragraphs.append(para)
                else:
                    break

        result = "\n\n".join(result_paragraphs)

        # 如果还是太长，简单截断
        if len(result) > max_length:
            result = result[:max_length-3] + "..."

        return result


# 便捷函数
def build_context_for_generation(
    current_chapter: int,
    chapter_outline: str,
    chapter_desc: str,
    character_tracker: CharacterTracker,
    plot_manager: PlotManager,
    world_db: WorldDatabase,
    api_client,
    max_length: int = 2000
) -> str:
    """
    便捷函数：构建生成上下文

    Args:
        current_chapter: 当前章节号
        chapter_outline: 章节大纲
        chapter_desc: 章节描述
        character_tracker: 角色跟踪器
        plot_manager: 剧情管理器
        world_db: 世界观数据库
        api_client: API客户端
        max_length: 最大长度

    Returns:
        上下文文本
    """
    builder = ContextBuilder(
        character_tracker,
        plot_manager,
        world_db,
        api_client
    )

    return builder.build_generation_context(
        current_chapter,
        chapter_outline,
        chapter_desc,
        max_length
    )
