"""
优化后的章节生成示例
展示如何使用所有新优化的提示词系统

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
"""

import logging
from typing import List, Dict

# 导入优化后的提示词系统
from src.core.prompts import (
    get_system_prompt,
    get_advanced_template,
    get_technique_example,
    COMMON_TECHNIQUES
)
from src.core.prompts.scene_planner import (
    ScenePlanner,
    build_scene_based_prompt
)
from src.core.coherence.character_tracker import CharacterTracker

logger = logging.getLogger(__name__)


class OptimizedChapterGenerator:
    """
    优化后的章节生成器

    集成所有优先级1和优先级2的优化
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def generate_chapter_optimized(
        self,
        project_id: str,
        chapter_num: int,
        chapter_title: str,
        chapter_desc: str,
        target_words: int,
        genre: str,
        previous_chapters: List[Dict],
        character_tracker: CharacterTracker
    ) -> str:
        """
        生成优化后的章节

        Args:
            project_id: 项目ID
            chapter_num: 章节号
            chapter_title: 章节标题
            chapter_desc: 章节描述
            target_words: 目标字数
            genre: 小说类型
            previous_chapters: 前面章节列表
            character_tracker: 角色跟踪器

        Returns:
            生成的章节内容
        """
        # ========== 优化1：使用高级 System Prompt ==========
        system_prompt = get_system_prompt("novel_writer", genre=genre)
        logger.info(f"使用 System Prompt: novel_writer ({genre})")

        # ========== 优化2：加入前一章尾部原文 ==========
        context_text = self._build_context_with_prev_tail(
            chapter_num, previous_chapters, tail_chars=800
        )

        # ========== 优化3：使用场景拆分策略 ==========
        scenes = ScenePlanner.plan_scenes(
            target_words=target_words,
            chapter_desc=chapter_desc
        )
        logger.info(f"规划了 {len(scenes)} 个场景")

        # ========== 优化4：连贯性系统信息（含 next_chapter_note） ==========
        coherence_info = self._build_coherence_info(
            character_tracker, chapter_num
        )

        # ========== 构建完整的 User Prompt ==========
        user_prompt = self._build_full_prompt(
            chapter_title=chapter_title,
            chapter_desc=chapter_desc,
            scenes=scenes,
            context_text=context_text,
            coherence_info=coherence_info,
            target_words=target_words
        )

        # ========== 调用 API ==========
        response = self.api_client.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.8, max_tokens=self._calculate_max_tokens(target_words))

        return response

    def _build_context_with_prev_tail(
        self,
        chapter_num: int,
        previous_chapters: List[Dict],
        tail_chars: int
    ) -> str:
        """构建包含前一章尾部的上下文"""
        if chapter_num <= 1 or not previous_chapters:
            return "【这是第一章，直接开始创作】"

        context_parts = []

        # 添加前一章尾部
        last_chapter = previous_chapters[-1]
        last_content = last_chapter.get("content", "")
        if last_content and len(last_content) > tail_chars:
            chapter_tail = last_content[-tail_chars:]
            context_parts.append("【前文结尾】")
            context_parts.append(f"以下是第{last_chapter['num']}章《{last_chapter.get('title', '')}》的最后部分，请从这里自然衔接：")
            context_parts.append("..." + chapter_tail)
            context_parts.append("")

        # 添加前文摘要
        context_parts.append("【前文摘要】")
        for ch in previous_chapters[-5:]:
            summary = ch.get("summary", "")
            if summary:
                context_parts.append(f"第{ch['num']}章 {ch.get('title', '')}: {summary}")

        return "\n".join(context_parts)

    def _build_coherence_info(
        self,
        character_tracker: CharacterTracker,
        chapter_num: int
    ) -> str:
        """构建连贯性信息（包含 next_chapter_note）"""
        info_parts = []

        # 角色状态
        if character_tracker and character_tracker.all_characters:
            info_parts.append("【主要角色】")
            for char_name in list(character_tracker.all_characters)[:5]:
                summary = character_tracker.get_character_summary_for_context(
                    char_name, chapter_num - 1
                )
                if summary:
                    info_parts.append(summary)

        # 下一章注意事项（新增！）
        if character_tracker:
            notes = character_tracker.get_all_next_chapter_notes(chapter_num)
            if notes:
                info_parts.append("\n" + notes)

        return "\n".join(info_parts)

    def _build_full_prompt(
        self,
        chapter_title: str,
        chapter_desc: str,
        scenes: List[Dict],
        context_text: str,
        coherence_info: str,
        target_words: int
    ) -> str:
        """构建完整的提示词"""
        prompt_parts = [context_text]

        if coherence_info:
            prompt_parts.append("\n" + coherence_info)

        prompt_parts.append(f"\n【当前章节】")
        prompt_parts.append(f"第{chapter_title.split()[0] if '章' in chapter_title else ''}章：{chapter_title}")
        prompt_parts.append(f"\n【章节要求】")
        prompt_parts.append(chapter_desc)

        # 场景拆分说明
        prompt_parts.append(f"\n【章节结构规划】")
        prompt_parts.append(f"本章共分{len(scenes)}个场景，总字数约{target_words}字：\n")
        for scene in scenes:
            prompt_parts.append(
                f"场景{scene['order']}：{scene['name']}（约{scene['target_words']}字）\n"
                f"- 目的：{scene['purpose']}\n"
                f"- 要素：{', '.join(scene['key_elements'])}"
            )

        prompt_parts.append(f"\n【创作要求】")
        prompt_parts.append(f"1. 严格按照场景规划执行，每个场景控制在指定字数范围±10%")
        prompt_parts.append(f"2. 场景之间要有自然的过渡衔接")
        prompt_parts.append(f"3. 整体字数控制在约{target_words}字")
        prompt_parts.append(f"\n请开始创作，请按场景顺序逐步展开：")

        return "\n".join(prompt_parts)

    def _calculate_max_tokens(self, target_words: int) -> int:
        """计算最大 tokens"""
        # 中文字符约等于 1.5 tokens
        return int(target_words * 1.5 * 1.3)  # 1.3是安全系数


class OptimizedRewriteGenerator:
    """
    优化后的重写生成器
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def rewrite_with_techniques(
        self,
        content: str,
        style: str = "默认",
        genre: str = None
    ) -> str:
        """
        使用技法指导进行重写

        Args:
            content: 原始内容
            style: 重写风格
            genre: 小说类型（可选）

        Returns:
            重写后的内容
        """
        # 获取高级重写模板（包含技法指导）
        template = get_advanced_template("rewrite", style)
        user_prompt = template.format(content=content)

        # 获取 genre 专属的 system prompt
        system_prompt = get_system_prompt("editor")
        if genre:
            genre_prompt = get_system_prompt("editor", genre=genre)
            system_prompt = f"{system_prompt}\n\n{genre_prompt}"

        response = self.api_client.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], temperature=0.7)

        return response


class OptimizedPolishGenerator:
    """
    优化后的润色生成器（带 Few-shot）
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def polish_with_examples(
        self,
        text: str,
        polish_type: str = "general"
    ) -> str:
        """
        使用 Few-shot 示例进行润色

        Args:
            text: 待润色文本
            polish_type: 润色类型

        Returns:
            润色后的文本
        """
        from src.ui.features.polish_advanced import get_polish_prompt_with_examples

        # 获取带示例的润色提示词
        prompt = get_polish_prompt_with_examples(polish_type, text)

        # 获取对应的 system prompt
        system_prompt_map = {
            "general": "你是一位资深的文学编辑。",
            "enhance_details": "你是一位擅长细节描写的作家。",
            "optimize_dialogue": "你是一位对话写作专家。",
            "improve_pacing": "你是一位节奏把控大师。",
        }
        system_prompt = system_prompt_map.get(polish_type, "你是一位专业的文学编辑。")

        response = self.api_client.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ], temperature=0.5)

        return response


# 使用示例
if __name__ == "__main__":
    # 模拟 API 客户端
    class MockAPIClient:
        def generate(self, messages, temperature=0.7, max_tokens=4000):
            return "这是模拟的生成结果..."

    api_client = MockAPIClient()

    # 示例1：优化后的章节生成
    generator = OptimizedChapterGenerator(api_client)
    tracker = CharacterTracker("test_project")

    result = generator.generate_chapter_optimized(
        project_id="test_project",
        chapter_num=6,
        chapter_title="第6章 突破境界",
        chapter_desc="林风在悬崖边闭关修炼，终于突破到筑基期，但引来雷劫",
        target_words=3000,
        genre="玄幻",
        previous_chapters=[
            {"num": 5, "title": "初入仙门", "content": "..." * 1000, "summary": "林风参加入门测试"}
        ],
        character_tracker=tracker
    )
    print("章节生成完成")

    # 示例2：优化后的重写
    rewriter = OptimizedRewriteGenerator(api_client)
    rewritten = rewriter.rewrite_with_techniques(
        content="少年走进森林，看到一只兔子。",
        style="玄幻仙侠",
        genre="玄幻"
    )
    print("重写完成")

    # 示例3：优化后的润色
    polisher = OptimizedPolishGenerator(api_client)
    polished = polisher.polish_with_examples(
        text="房间里很乱。",
        polish_type="enhance_details"
    )
    print("润色完成")
