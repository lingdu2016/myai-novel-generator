"""
优化生成器 - 整合所有优化系统

核心功能：
1. 增强的上下文构建
2. AI味道检测与消除
3. 章节质量评估
4. 自动优化和修正

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import logging
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from datetime import datetime
import json

from .enhanced_context import EnhancedContextBuilder, ForeshadowingManager, ChapterTransitionGenerator
from .style_optimizer import StyleOptimizer, detect_and_optimize, get_style_score
from .quality_assessor import QualityAssessor, assess_chapter_quality
from .coherence.hierarchical_summary import HierarchicalSummaryManager

logger = logging.getLogger(__name__)


class OptimizedNovelGenerator:
    """优化的小说生成器"""

    def __init__(
        self,
        api_client,
        summary_manager: HierarchicalSummaryManager,
        character_tracker,
        plot_manager,
        world_db,
        project_dir: Path,
        cache_dir: Optional[Path] = None
    ):
        """
        初始化优化生成器

        Args:
            api_client: API客户端
            summary_manager: 分层摘要管理器
            character_tracker: 角色跟踪器
            plot_manager: 剧情管理器
            world_db: 世界观数据库
            project_dir: 项目目录
            cache_dir: 缓存目录
        """
        self.api_client = api_client
        self.summary_manager = summary_manager
        self.character_tracker = character_tracker
        self.plot_manager = plot_manager
        self.world_db = world_db
        self.project_dir = project_dir
        self.cache_dir = cache_dir or Path("cache/optimized")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 初始化子系统
        self.context_builder = EnhancedContextBuilder(
            summary_manager,
            character_tracker,
            plot_manager,
            world_db,
            api_client
        )

        self.foreshadowing_manager = ForeshadowingManager(plot_manager, api_client)
        self.transition_generator = ChapterTransitionGenerator(api_client)
        self.style_optimizer = StyleOptimizer(api_client)
        self.quality_assessor = QualityAssessor(api_client)

        # 生成配置
        self.generation_config = {
            "enable_style_optimization": True,  # 启用风格优化
            "enable_quality_assessment": True,  # 启用质量评估
            "style_optimization_mode": "auto",  # auto/ai_off/ai_on
            "min_quality_score": 70.0,  # 最低质量分数
            "max_optimization_attempts": 2,  # 最大优化尝试次数
        }

        # 统计信息
        self.stats = {
            "total_chapters": 0,
            "optimized_chapters": 0,
            "avg_quality_score": 0.0,
            "avg_style_score": 0.0,
        }

    def generate_optimized_chapter(
        self,
        chapter_num: int,
        chapter_title: str,
        chapter_desc: str,
        target_words: int,
        previous_chapters: List[Dict],
        generation_params: Optional[Dict] = None
    ) -> Tuple[bool, str, Dict]:
        """
        生成优化的章节

        Args:
            chapter_num: 章节号
            chapter_title: 章节标题
            chapter_desc: 章节描述
            target_words: 目标字数
            previous_chapters: 前面章节列表
            generation_params: 生成参数（可选）

        Returns:
            (成功标志, 消息, 章节数据)
        """
        logger.info(f"[优化生成器] 开始生成第{chapter_num}章: {chapter_title}")

        try:
            # 1. 构建增强上下文
            context = self.context_builder.build_smart_context(
                chapter_num=chapter_num,
                chapter_outline=chapter_desc,
                previous_chapters=previous_chapters
            )

            # 2. 构建生成提示词
            prompt = self._build_generation_prompt(
                chapter_num=chapter_num,
                chapter_title=chapter_title,
                chapter_desc=chapter_desc,
                context=context,
                target_words=target_words
            )

            # 3. 调用API生成
            generation_params = generation_params or {}
            temperature = generation_params.get("temperature", 0.8)
            max_tokens = generation_params.get("max_tokens", int(target_words * 1.3))

            raw_content = self.api_client.generate([
                {"role": "system", "content": "你是一位专业的小说作家。"},
                {"role": "user", "content": prompt}
            ], temperature=temperature, max_tokens=max_tokens)

            if not raw_content or len(raw_content.strip()) < 100:
                return False, "生成内容过短", {}

            logger.info(f"[优化生成器] 第{chapter_num}章原始内容生成完成，字数: {len(raw_content)}")

            # 4. 风格优化
            optimized_content = raw_content
            style_report = {}

            if self.generation_config["enable_style_optimization"]:
                optimized_content, style_report = self._optimize_content(
                    raw_content,
                    chapter_num
                )

            # 5. 质量评估
            quality_report = {}
            if self.generation_config["enable_quality_assessment"]:
                quality_report = self.quality_assessor.assess_chapter(
                    content=optimized_content,
                    chapter_num=chapter_num,
                    chapter_outline=chapter_desc,
                    previous_summary=self._get_previous_summary(previous_chapters)
                )

                # 如果质量不达标，尝试重新生成
                if quality_report["total_score"] < self.generation_config["min_quality_score"]:
                    logger.warning(f"第{chapter_num}章质量不达标 ({quality_report['total_score']:.1f})，尝试重新生成")
                    optimized_content, style_report, quality_report = self._regenerate_chapter(
                        chapter_num,
                        chapter_title,
                        chapter_desc,
                        target_words,
                        previous_chapters,
                        quality_report
                    )

            # 6. 更新统计信息
            self._update_stats(style_report, quality_report)

            # 7. 构建章节数据
            chapter_data = {
                "num": chapter_num,
                "title": chapter_title,
                "desc": chapter_desc,
                "content": optimized_content,
                "word_count": len(optimized_content),
                "generated_at": datetime.now().isoformat(),
                "optimization_report": style_report,
                "quality_report": quality_report,
            }

            # 8. 生成摘要
            chapter_data["summary"] = self._generate_chapter_summary(optimized_content)

            logger.info(f"[优化生成器] 第{chapter_num}章生成完成，最终字数: {len(optimized_content)}")

            return True, "生成成功", chapter_data

        except Exception as e:
            logger.error(f"[优化生成器] 第{chapter_num}章生成失败: {e}", exc_info=True)
            return False, f"生成失败: {str(e)}", {}

    def _build_generation_prompt(
        self,
        chapter_num: int,
        chapter_title: str,
        chapter_desc: str,
        context: str,
        target_words: int
    ) -> str:
        """构建生成提示词"""
        prompt = f"""请根据以下信息创作小说章节。

{context}

【当前章节】
第{chapter_num}章：{chapter_title}

【章节要求】
{chapter_desc}

【创作要求】
1. 目标字数：约 {target_words} 字（可在±500字范围内浮动）
2. 保持与前文的连贯性
3. 角色性格和行为要一致
4. 情节发展要自然
5. 注意环境描写的连贯性

【风格要求】（重要）
- 不要使用AI化的表达（突然、竟然、心中涌起等）
- 对话要口语化，像真人说话
- 描写要具体，用细节代替空洞形容词
- 不要在结尾总结人生感悟
- 保持自然流畅的文风

请开始创作本章内容："""

        return prompt

    def _optimize_content(
        self,
        content: str,
        chapter_num: int
    ) -> Tuple[str, Dict]:
        """
        优化内容风格

        Args:
            content: 原始内容
            chapter_num: 章节号

        Returns:
            (优化后的内容, 优化报告)
        """
        mode = self.generation_config["style_optimization_mode"]

        if mode == "ai_off":
            # 仅本地优化
            return self.style_optimizer.optimize_chapter(content, auto_correct=True)
        elif mode == "ai_on":
            # AI辅助优化
            return self.style_optimizer.optimize_with_ai(content)
        else:
            # 自动模式：根据质量决定
            score, grade = get_style_score(content)

            if score >= 85:
                # 质量已经很好，仅本地优化
                logger.info(f"第{chapter_num}章风格评分 {score:.1f} ({grade})，使用本地优化")
                return self.style_optimizer.optimize_chapter(content, auto_correct=True)
            else:
                # 质量一般，使用AI优化
                logger.info(f"第{chapter_num}章风格评分 {score:.1f} ({grade})，使用AI优化")
                return self.style_optimizer.optimize_with_ai(content)

    def _regenerate_chapter(
        self,
        chapter_num: int,
        chapter_title: str,
        chapter_desc: str,
        target_words: int,
        previous_chapters: List[Dict],
        original_quality_report: Dict
    ) -> Tuple[str, Dict, Dict]:
        """
        重新生成章节（质量不达标时）

        Args:
            chapter_num: 章节号
            chapter_title: 章节标题
            chapter_desc: 章节描述
            target_words: 目标字数
            previous_chapters: 前面章节列表
            original_quality_report: 原始质量报告

        Returns:
            (优化后的内容, 风格报告, 质量报告)
        """
        max_attempts = self.generation_config["max_optimization_attempts"]

        for attempt in range(max_attempts):
            logger.info(f"第{chapter_num}章重新生成尝试 {attempt + 1}/{max_attempts}")

            # 提取主要问题
            main_issues = original_quality_report["overall_suggestions"][:3]

            # 构建改进提示词
            improvement_prompt = f"""请根据以下反馈改进章节内容。

【原文】
（略）

【主要问题】
{chr(10).join(f'- {issue}' for issue in main_issues)}

【章节信息】
第{chapter_num}章：{chapter_title}
要求：{chapter_desc}
目标字数：约{target_words}字

请重新创作，解决上述问题："""

            # 重新生成
            new_content = self.api_client.generate([
                {"role": "system", "content": "你是一位专业的小说作家，擅长根据反馈改进作品。"},
                {"role": "user", "content": improvement_prompt}
            ], temperature=0.8, max_tokens=int(target_words * 1.3))

            if new_content:
                # 重新评估
                style_report = self._optimize_content(new_content, chapter_num)
                quality_report = self.quality_assessor.assess_chapter(
                    content=new_content,
                    chapter_num=chapter_num,
                    chapter_outline=chapter_desc,
                    previous_summary=self._get_previous_summary(previous_chapters)
                )

                # 检查是否达标
                if quality_report["total_score"] >= self.generation_config["min_quality_score"]:
                    logger.info(f"第{chapter_num}章重新生成成功，质量: {quality_report['total_score']:.1f}")
                    return new_content, style_report, quality_report
                else:
                    logger.warning(f"第{chapter_num}章重新生成后质量仍不达标: {quality_report['total_score']:.1f}")
            else:
                logger.warning(f"第{chapter_num}章重新生成失败")

        # 所有尝试都失败，返回最好的结果
        logger.warning(f"第{chapter_num}章所有重新生成尝试都失败，返回原始结果")
        return "", {}, original_quality_report

    def _get_previous_summary(self, previous_chapters: List[Dict]) -> str:
        """获取前文摘要"""
        if not previous_chapters:
            return ""

        # 获取最近3章的摘要
        recent_chapters = previous_chapters[-3:]
        summaries = []

        for ch in recent_chapters:
            summary = ch.get("summary", "")
            if summary:
                summaries.append(f"第{ch['num']}章: {summary}")

        return "\n".join(summaries)

    def _generate_chapter_summary(self, content: str, max_length: int = 100) -> str:
        """生成章节摘要"""
        # 简化处理：使用开头和结尾
        if len(content) <= 200:
            return content

        start = content[:100]
        end = content[-100:]

        # 使用API生成摘要
        try:
            summary = self.api_client.generate([
                {"role": "system", "content": "你是一个专业的小说摘要助手。"},
                {"role": "user", "content": f"请用一句话总结以下章节的主要内容（{max_length}字以内）：\n开头：{start}\n结尾：{end}"}
            ], temperature=0.3, max_tokens=200)

            return summary.strip() if summary else content[:max_length]
        except Exception as e:
            logger.warning(f"生成摘要失败: {e}")
            return content[:max_length]

    def _update_stats(self, style_report: Dict, quality_report: Dict) -> None:
        """更新统计信息"""
        self.stats["total_chapters"] += 1

        if style_report and style_report.get("auto_corrected"):
            self.stats["optimized_chapters"] += 1

        if quality_report:
            total_score = quality_report.get("total_score", 0)
            avg_score = self.stats.get("avg_quality_score", 0)

            # 计算新的平均值
            count = self.stats["total_chapters"]
            new_avg = (avg_score * (count - 1) + total_score) / count
            self.stats["avg_quality_score"] = round(new_avg, 1)

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """重置统计信息"""
        self.stats = {
            "total_chapters": 0,
            "optimized_chapters": 0,
            "avg_quality_score": 0.0,
            "avg_style_score": 0.0,
        }


# 便捷函数
def create_optimized_generator(
    api_client,
    summary_manager: HierarchicalSummaryManager,
    character_tracker,
    plot_manager,
    world_db,
    project_dir: Path,
    cache_dir: Optional[Path] = None
) -> OptimizedNovelGenerator:
    """创建优化生成器"""
    return OptimizedNovelGenerator(
        api_client,
        summary_manager,
        character_tracker,
        plot_manager,
        world_db,
        project_dir,
        cache_dir
    )
