"""
增强的上下文构建系统

核心改进：
1. 智能摘要系统（多级摘要）
2. 上下文相关度评分
3. 章节过渡机制
4. 悬念和伏笔管理

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json

from .coherence.hierarchical_summary import HierarchicalSummaryManager
from .coherence.character_tracker import CharacterTracker
from .coherence.plot_manager import PlotManager
from .coherence.world_db import WorldDatabase

logger = logging.getLogger(__name__)


class EnhancedContextBuilder:
    """增强的上下文构建器"""

    def __init__(
        self,
        summary_manager: HierarchicalSummaryManager,
        character_tracker: CharacterTracker,
        plot_manager: PlotManager,
        world_db: WorldDatabase,
        api_client
    ):
        """
        初始化增强上下文构建器

        Args:
            summary_manager: 分层摘要管理器
            character_tracker: 角色跟踪器
            plot_manager: 剧情管理器
            world_db: 世界观数据库
            api_client: API客户端
        """
        self.summary_manager = summary_manager
        self.character_tracker = character_tracker
        self.plot_manager = plot_manager
        self.world_db = world_db
        self.api_client = api_client

        # 上下文配置
        self.context_config = {
            "max_context_length": 3000,  # 最大上下文长度
            "relevant_chapters": 5,  # 相关章节数
            "include_arc_summaries": True,  # 是否包含卷摘要
            "include_character_states": True,  # 是否包含角色状态
            "include_plot_threads": True,  # 是否包含剧情线
            "include_unresolved_foreshadowing": True,  # 是否包含未解决伏笔
        }

    def build_smart_context(
        self,
        chapter_num: int,
        chapter_outline: str,
        previous_chapters: List[Dict],
        max_tokens: int = 4000
    ) -> str:
        """
        智能构建上下文

        Args:
            chapter_num: 当前章节号
            chapter_outline: 章节大纲
            previous_chapters: 前面章节列表
            max_tokens: 最大token数

        Returns:
            上下文文本
        """
        logger.info(f"[增强上下文] 开始为第{chapter_num}章构建上下文")

        context_parts = []

        # 1. 基础信息
        context_parts.append(self._build_basic_info(chapter_num))

        # 2. 分层摘要（核心）
        if self.summary_manager and self.context_config["include_arc_summaries"]:
            arc_context = self._build_arc_summaries(chapter_num, previous_chapters)
            if arc_context:
                context_parts.append(arc_context)

        # 3. 最近章节详情
        recent_context = self._build_recent_chapters(chapter_num, previous_chapters)
        if recent_context:
            context_parts.append(recent_context)

        # 4. 角色状态
        if self.context_config["include_character_states"]:
            char_context = self._build_character_context(chapter_num)
            if char_context:
                context_parts.append(char_context)

        # 5. 剧情线
        if self.context_config["include_plot_threads"]:
            plot_context = self._build_plot_context(chapter_num)
            if plot_context:
                context_parts.append(plot_context)

        # 6. 未解决伏笔和悬念
        if self.context_config["include_unresolved_foreshadowing"]:
            foreshadowing_context = self._build_foreshadowing_context(chapter_num)
            if foreshadowing_context:
                context_parts.append(foreshadowing_context)

        # 7. 章节过渡（桥梁）
        bridge_context = self._build_chapter_bridge(chapter_num, previous_chapters)
        if bridge_context:
            context_parts.append(bridge_context)

        # 组装上下文
        full_context = "\n\n".join(context_parts)

        # 截断到合适长度
        if len(full_context) > self.context_config["max_context_length"]:
            full_context = self._smart_truncate(full_context, self.context_config["max_context_length"])

        logger.info(f"[增强上下文] 第{chapter_num}章上下文构建完成，长度: {len(full_context)} 字符")

        return full_context

    def _build_basic_info(self, chapter_num: int) -> str:
        """构建基础信息"""
        if chapter_num == 1:
            return "【小说起始】\n这是第一章，请直接开始创作。"
        else:
            return f"【当前章节】\n第{chapter_num}章"

    def _build_arc_summaries(self, chapter_num: int, previous_chapters: List[Dict]) -> str:
        """构建卷摘要上下文"""
        if not self.summary_manager:
            return ""

        context_parts = ["【故事脉络】"]

        # 获取所有卷摘要
        stats = self.summary_manager.get_summary_stats()
        arc_count = stats.get('total_arcs', 0)

        if arc_count == 0:
            return ""

        # 获取当前卷之前的所有卷摘要
        current_arc_id = self.summary_manager.get_arc_id(chapter_num)

        for arc_id in range(1, current_arc_id):
            arc_summary = self.summary_manager.get_arc_summary(arc_id)
            if arc_summary:
                context_parts.append(f"第{arc_id}卷: {arc_summary.get('summary', '')}")

        # 获取当前卷的摘要（如果有）
        if current_arc_id > 1:
            current_arc_summary = self.summary_manager.get_arc_summary(current_arc_id)
            if current_arc_summary:
                context_parts.append(f"第{current_arc_id}卷（当前）: {current_arc_summary.get('summary', '')}")

        return "\n".join(context_parts) if len(context_parts) > 1 else ""

    def _build_recent_chapters(self, chapter_num: int, previous_chapters: List[Dict]) -> str:
        """构建最近章节上下文"""
        if not previous_chapters:
            return ""

        context_parts = ["【前文回顾】"]

        # 获取最近5章
        recent_chapters = previous_chapters[-5:]

        for ch in recent_chapters:
            ch_num = ch.get('num', 0)
            ch_title = ch.get('title', '')
            ch_content = ch.get('content', '')
            ch_summary = ch.get('summary', '')

            # 如果有摘要，使用摘要
            if ch_summary:
                context_parts.append(f"第{ch_num}章《{ch_title}》: {ch_summary}")
            # 否则，使用最后200字
            elif ch_content:
                tail = ch_content[-200:] if len(ch_content) > 200 else ch_content
                context_parts.append(f"第{ch_num}章《{ch_title}》（结尾）: ...{tail}")
            else:
                context_parts.append(f"第{ch_num}章《{ch_title}》")

        return "\n".join(context_parts)

    def _build_character_context(self, chapter_num: int) -> str:
        """构建角色上下文"""
        if not self.character_tracker:
            return ""

        context_parts = ["【角色状态】"]

        # 获取活跃角色（最近出现过的）
        active_characters = self.character_tracker.get_recent_characters(chapter_num - 1, limit=5)

        for char_name in active_characters:
            char_state = self.character_tracker.get_character_current_state(char_name)
            if char_state:
                location = char_state.location or "未知"
                status = char_state.status or ""
                personality = char_state.personality or ""

                info = f"- {char_name}: {location}"
                if status:
                    info += f"，状态：{status}"
                if personality:
                    info += f"，性格：{personality}"

                context_parts.append(info)

        return "\n".join(context_parts) if len(context_parts) > 1 else ""

    def _build_plot_context(self, chapter_num: int) -> str:
        """构建剧情线上下文"""
        if not self.plot_manager:
            return ""

        context_parts = ["【剧情进展】"]

        # 获取活跃剧情线
        active_threads = self.plot_manager.get_active_threads()

        for thread in active_threads[:3]:
            thread_name = thread.name
            thread_status = thread.status

            # 获取最近事件
            recent_events = [
                event for event in thread.key_events
                if event.chapter_num < chapter_num
            ]
            if recent_events:
                last_event = recent_events[-1]
                context_parts.append(f"- {thread_name}（{thread_status}）: {last_event.description}")

                # 未解决的伏笔
                foreshadowing = self.plot_manager.get_unresolved_foreshadowing(thread.id)
                if foreshadowing:
                    context_parts.append(f"  未解决伏笔: {foreshadowing[0]}")

        return "\n".join(context_parts) if len(context_parts) > 1 else ""

    def _build_foreshadowing_context(self, chapter_num: int) -> str:
        """构建伏笔和悬念上下文"""
        if not self.plot_manager:
            return ""

        context_parts = ["【待解决要素】"]

        # 未解决的伏笔
        all_foreshadowing = self.plot_manager.get_unresolved_foreshadowing()
        if all_foreshadowing:
            context_parts.append(f"未解决伏笔（共{len(all_foreshadowing)}个）:")
            for fs in all_foreshadowing[:3]:
                context_parts.append(f"  - {fs}")

        # 未解决的悬念
        all_cliffhangers = self.plot_manager.get_unresolved_cliffhangers()
        if all_cliffhangers:
            context_parts.append(f"\n未解决悬念（共{len(all_cliffhangers)}个）:")
            for ch in all_cliffhangers[:2]:
                context_parts.append(f"  - {ch}")

        return "\n".join(context_parts) if len(context_parts) > 1 else ""

    def _build_chapter_bridge(self, chapter_num: int, previous_chapters: List[Dict]) -> str:
        """构建章节过渡（桥梁）"""
        if not previous_chapters or chapter_num == 1:
            return ""

        last_chapter = previous_chapters[-1]
        last_chapter_num = last_chapter.get('num', 0)
        last_chapter_title = last_chapter.get('title', '')
        last_chapter_content = last_chapter.get('content', '')

        if not last_chapter_content:
            return ""

        # 提取最后一段
        paragraphs = last_chapter_content.split('\n\n')
        if not paragraphs:
            return ""

        last_paragraph = paragraphs[-1]
        if len(last_paragraph) < 50:
            return ""

        # 检查是否有悬念
        cliffhanger_indicators = ['？', '！', '...', '突然', '就在这时', '忽然']
        has_cliffhanger = any(indicator in last_paragraph for indicator in cliffhanger_indicators)

        if has_cliffhanger:
            return f"""【章节衔接】
第{last_chapter_num}章《{last_chapter_title}》结尾：
{last_paragraph}

请从以上结尾自然衔接，不要重复描述，直接继续情节。"""
        else:
            # 平滑过渡
            return f"""【章节衔接】
第{last_chapter_num}章《{last_chapter_title}》已结束。
请自然开始第{chapter_num}章的情节。"""

    def _smart_truncate(self, text: str, max_length: int) -> str:
        """智能截断文本"""
        if len(text) <= max_length:
            return text

        # 按段落分割
        paragraphs = text.split('\n\n')

        # 优先保留高优先级段落
        priority_keywords = ["【故事脉络】", "【角色状态】", "【剧情进展】", "【待解决要素】"]
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


class ForeshadowingManager:
    """伏笔和悬念管理器"""

    def __init__(self, plot_manager: PlotManager, api_client):
        """
        初始化伏笔管理器

        Args:
            plot_manager: 剧情管理器
            api_client: API客户端
        """
        self.plot_manager = plot_manager
        self.api_client = api_client

    def extract_foreshadowing(
        self,
        chapter_content: str,
        chapter_num: int
    ) -> List[str]:
        """
        从章节中提取伏笔

        Args:
            chapter_content: 章节内容
            chapter_num: 章节号

        Returns:
            伏笔列表
        """
        prompt = f"""分析以下章节内容，提取其中的伏笔。

章节内容：
{chapter_content[-1000:]}

请以JSON格式返回：
{{
    "foreshadowing": ["伏笔1", "伏笔2", "伏笔3"]
}}

只返回JSON，不要其他文字。"""

        try:
            response = self.api_client.generate([
                {"role": "system", "content": "你是一个专业的小说编辑，擅长识别故事中的伏笔。"},
                {"role": "user", "content": prompt}
            ], temperature=0.3, max_tokens=500)

            if response:
                import json
                import re
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    result = json.loads(json_match.group())
                    return result.get("foreshadowing", [])
        except Exception as e:
            logger.warning(f"提取伏笔失败: {e}")

        return []

    def check_unresolved_foreshadowing(
        self,
        chapter_num: int,
        max_age: int = 20
    ) -> List[Dict]:
        """
        检查未解决的伏笔

        Args:
            chapter_num: 当前章节号
            max_age: 最大章节数（超过这个章节数的伏笔需要提醒）

        Returns:
            未解决伏笔列表，包含章节号和内容
        """
        unresolved = []

        all_foreshadowing = self.plot_manager.get_unresolved_foreshadowing()
        # 这里需要扩展plot_manager来支持获取伏笔的章节号
        # 暂时返回空列表

        return unresolved


class ChapterTransitionGenerator:
    """章节过渡生成器"""

    def __init__(self, api_client):
        """
        初始化过渡生成器

        Args:
            api_client: API客户端
        """
        self.api_client = api_client

    def generate_transition(
        self,
        prev_chapter_end: str,
        next_chapter_outline: str,
        transition_style: str = "smooth"
    ) -> str:
        """
        生成章节过渡

        Args:
            prev_chapter_end: 前一章结尾
            next_chapter_outline: 下一章大纲
            transition_style: 过渡风格（smooth/cliffhanger/time_skip）

        Returns:
            过渡文本
        """
        if transition_style == "cliffhanger":
            style_desc = "制造悬念，让读者想知道接下来会发生什么"
        elif transition_style == "time_skip":
            style_desc = "时间跳跃，直接进入新场景"
        else:
            style_desc = "平滑过渡，自然衔接"

        prompt = f"""请为以下章节生成过渡段落。

前一章结尾：
{prev_chapter_end[-500:]}

下一章大纲：
{next_chapter_outline}

过渡风格：{style_desc}

要求：
- 2-3句话
- 不要重复前一章的内容
- 引出下一章的情节
- 保持风格一致

过渡段落："""

        try:
            response = self.api_client.generate([
                {"role": "system", "content": "你是一个专业的小说作家，擅长章节过渡。"},
                {"role": "user", "content": prompt}
            ], temperature=0.7, max_tokens=200)

            return response.strip() if response else ""
        except Exception as e:
            logger.warning(f"生成过渡失败: {e}")
            return ""


# 便捷函数
def create_enhanced_context_builder(
    summary_manager: HierarchicalSummaryManager,
    character_tracker: CharacterTracker,
    plot_manager: PlotManager,
    world_db: WorldDatabase,
    api_client
) -> EnhancedContextBuilder:
    """创建增强上下文构建器"""
    return EnhancedContextBuilder(
        summary_manager,
        character_tracker,
        plot_manager,
        world_db,
        api_client
    )
