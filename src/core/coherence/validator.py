"""
连贯性验证器 - AI驱动的连贯性检查，确保章节逻辑一致

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .character_tracker import CharacterTracker
from .plot_manager import PlotManager
from .world_db import WorldDatabase

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """验证问题"""
    severity: str                  # 严重程度（error/warning/info）
    category: str                  # 类别（character/plot/world/logic）
    description: str               # 问题描述
    location: str = ""             # 位置（章节号或段落）
    suggestion: str = ""           # 修改建议
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool                 # 是否通过验证
    issues: List[ValidationIssue]  # 问题列表
    score: float = 0.0             # 连贯性评分（0-100）
    summary: str = ""              # 总结


class CoherenceValidator:
    """
    连贯性验证器

    功能：
    1. 检查角色性格一致性
    2. 检查角色位置合理性
    3. 检查剧情逻辑连贯性
    4. 检查伏笔和悬念的呼应
    5. 检查世界观设定自洽性
    """

    def __init__(
        self,
        character_tracker: CharacterTracker,
        plot_manager: PlotManager,
        world_db: WorldDatabase,
        api_client
    ):
        """
        初始化验证器

        Args:
            character_tracker: 角色跟踪器
            plot_manager: 剧情管理器
            world_db: 世界观数据库
            api_client: API客户端（用于AI验证）
        """
        self.character_tracker = character_tracker
        self.plot_manager = plot_manager
        self.world_db = world_db
        self.api_client = api_client

    def validate_chapter(
        self,
        chapter_content: str,
        chapter_num: int,
        chapter_outline: str = ""
    ) -> ValidationResult:
        """
        验证章节连贯性

        Args:
            chapter_content: 章节内容
            chapter_num: 章节号
            chapter_outline: 章节大纲（可选，用于对比）

        Returns:
            ValidationResult对象
        """
        issues = []

        logger.info(f"[连贯性验证] 开始验证第{chapter_num}章")
        logger.debug(f"[连贯性验证] 章节内容长度: {len(chapter_content)} 字符, 大纲长度: {len(chapter_outline)} 字符")

        # 1. 角色连贯性检查
        character_issues = self._check_character_coherence(
            chapter_content,
            chapter_num
        )
        issues.extend(character_issues)

        # 2. 剧情连贯性检查
        plot_issues = self._check_plot_coherence(
            chapter_content,
            chapter_num,
            chapter_outline
        )
        issues.extend(plot_issues)

        # 3. 世界观一致性检查
        world_issues = self._check_world_consistency(
            chapter_content,
            chapter_num
        )
        issues.extend(world_issues)

        # 4. AI深度验证
        ai_issues = self._ai_validate_chapter(
            chapter_content,
            chapter_num,
            chapter_outline
        )
        issues.extend(ai_issues)

        # 计算评分
        score = self._calculate_score(issues)

        # 生成总结
        summary = self._generate_summary(issues, score)

        # 判断是否通过
        error_count = sum(1 for i in issues if i.severity == "error")
        is_valid = error_count == 0

        logger.info(f"[连贯性验证] 第{chapter_num}章验证完成，评分: {score:.1f}, 问题数: {len(issues)}")
        if issues:
            logger.debug(f"[连贯性验证] 问题详情: {[f'{i.severity}:{i.category}' for i in issues[:5]]}...")

        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            score=score,
            summary=summary
        )

    def _check_character_coherence(
        self,
        chapter_content: str,
        chapter_num: int
    ) -> List[ValidationIssue]:
        """检查角色连贯性"""
        issues = []

        # 获取本章涉及的角色
        characters = self.character_tracker.get_characters_in_chapter(chapter_num)

        for char_name in characters:
            current_state = self.character_tracker.get_character_current_state(char_name)
            if not current_state:
                continue

            # 检查性格一致性（简化版本）
            # 实际应该使用AI进行语义分析

            # 检查是否有不合理的位置变化
            # 这里简化处理，实际需要更复杂的逻辑

        # 同时使用角色跟踪器的内置检测
        tracker_issues = self.character_tracker.detect_inconsistencies()
        for issue in tracker_issues:
            issues.append(ValidationIssue(
                severity="warning",
                category="character",
                description=issue,
                location=f"第{chapter_num}章",
                suggestion="请检查角色行为是否符合既定性格设定"
            ))

        return issues

    def _check_plot_coherence(
        self,
        chapter_content: str,
        chapter_num: int,
        chapter_outline: str
    ) -> List[ValidationIssue]:
        """检查剧情连贯性"""
        issues = []

        # 获取本章涉及的剧情线
        plot_threads = self.plot_manager.get_threads_in_chapter(chapter_num)

        # 检查是否有剧情线被遗忘（长时间未提及）
        for thread in self.plot_manager.get_active_threads():
            # 检查该剧情线是否应该在本章提及但未提及
            # 这里简化处理

            pass

        # 检查伏笔和悬念的处理
        unresolved_foreshadowing = self.plot_manager.get_unresolved_foreshadowing()
        if len(unresolved_foreshadowing) > 15:
            issues.append(ValidationIssue(
                severity="warning",
                category="plot",
                description=f"未解决的伏笔过多（{len(unresolved_foreshadowing)}个），可能导致读者混乱",
                location=f"第{chapter_num}章",
                suggestion="考虑在后续章节中解决部分伏笔"
            ))

        unresolved_cliffhangers = self.plot_manager.get_unresolved_cliffhangers()
        if len(unresolved_cliffhangers) > 8:
            issues.append(ValidationIssue(
                severity="warning",
                category="plot",
                description=f"未解决的悬念过多（{len(unresolved_cliffhangers)}个）",
                location=f"第{chapter_num}章",
                suggestion="建议及时解决悬念，避免堆积"
            ))

        # 使用剧情管理器的内置检测
        plot_issues = self.plot_manager.check_thread_continuity()
        for issue in plot_issues:
            issues.append(ValidationIssue(
                severity="info",
                category="plot",
                description=issue,
                location=f"第{chapter_num}章",
                suggestion="检查剧情线的推进节奏"
            ))

        return issues

    def _check_world_consistency(
        self,
        chapter_content: str,
        chapter_num: int
    ) -> List[ValidationIssue]:
        """检查世界观一致性"""
        issues = []

        # 使用世界观数据库的内置检查
        world_issues = self.world_db.check_consistency(chapter_content)

        for issue in world_issues:
            issues.append(ValidationIssue(
                severity="error",
                category="world",
                description=issue,
                location=f"第{chapter_num}章",
                suggestion="确保与已有世界观设定一致"
            ))

        return issues

    def _ai_validate_chapter(
        self,
        chapter_content: str,
        chapter_num: int,
        chapter_outline: str = ""
    ) -> List[ValidationIssue]:
        """使用AI进行深度验证"""
        issues = []

        logger.info(f"[AI验证] 开始第{chapter_num}章AI深度验证")

        # 准备上下文
        context_parts = []

        # 添加角色状态摘要
        characters = self.character_tracker.get_characters_in_chapter(chapter_num)
        if characters:
            context_parts.append("角色状态:")
            for char_name in characters[:3]:
                summary = self.character_tracker.get_character_summary_for_context(
                    char_name,
                    chapter_num - 1
                )
                if summary:
                    context_parts.append(summary)

        # 添加剧情线摘要
        plot_summary = self.plot_manager.get_plot_summary_for_context(chapter_num, max_length=300)
        if plot_summary:
            context_parts.append(plot_summary)

        # 添加世界观摘要
        world_summary = self.world_db.get_world_summary(max_items=3)
        if world_summary:
            context_parts.append(world_summary)

        context = "\n\n".join(context_parts)

        # 构建AI验证提示词
        prompt = f"""请检查以下章节内容的连贯性，找出可能的问题。

【章节信息】
章节号：第{chapter_num}章
章节大纲：{chapter_outline}

【历史上下文】
{context}

【本章内容】
{chapter_content[:1500]}

请检查以下方面：
1. 角色性格是否与之前一致
2. 角色位置变化是否合理
3. 剧情推进是否符合逻辑
4. 是否有应该提及但未提及的伏笔或悬念
5. 是否违反世界观设定

请以JSON格式返回问题列表：
{{
    "issues": [
        {{
            "severity": "error/warning/info",
            "category": "character/plot/world/logic",
            "description": "问题描述",
            "suggestion": "修改建议"
        }}
    ]
}}

如果未发现问题，返回 {{\"issues\": []}}。只返回JSON，不要其他文字。"""

        try:
            response = self.api_client.generate([
                {"role": "system", "content": "你是一个专业的小说编辑，擅长发现连贯性问题。"},
                {"role": "user", "content": prompt}
            ], temperature=0.3)

            import json
            result = json.loads(response)

            for issue_data in result.get("issues", []):
                issues.append(ValidationIssue(
                    severity=issue_data.get("severity", "info"),
                    category=issue_data.get("category", "logic"),
                    description=issue_data.get("description", ""),
                    location=f"第{chapter_num}章",
                    suggestion=issue_data.get("suggestion", "")
                ))

            logger.info(f"[AI验证] AI验证完成，发现 {len(issues)} 个问题")

        except Exception as e:
            logger.error(f"[AI验证] AI验证失败: {e}", exc_info=True)

        return issues

    def _calculate_score(self, issues: List[ValidationIssue]) -> float:
        """
        计算连贯性评分

        Args:
            issues: 问题列表

        Returns:
            评分（0-100）
        """
        if not issues:
            return 100.0

        # 根据问题严重程度扣分
        deductions = {
            "error": 20,
            "warning": 10,
            "info": 5
        }

        total_deduction = sum(
            deductions.get(issue.severity, 5)
            for issue in issues
        )

        score = max(0, 100 - total_deduction)
        return float(score)

    def _generate_summary(self, issues: List[ValidationIssue], score: float) -> str:
        """
        生成验证总结

        Args:
            issues: 问题列表
            score: 评分

        Returns:
            总结文本
        """
        if not issues:
            return f"✓ 连贯性验证通过，评分: {score:.1f}/100"

        # 统计各类问题
        by_severity = {}
        by_category = {}

        for issue in issues:
            # 按严重程度统计
            severity = issue.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1

            # 按类别统计
            category = issue.category
            by_category[category] = by_category.get(category, 0) + 1

        summary_parts = [
            f"连贯性评分: {score:.1f}/100",
            f"发现问题: {len(issues)}个"
        ]

        if by_severity:
            severity_text = ", ".join([
                f"{severity} {count}个"
                for severity, count in sorted(by_severity.items())
            ])
            summary_parts.append(f"按严重程度: {severity_text}")

        if by_category:
            category_text = ", ".join([
                f"{cat} {count}个"
                for cat, count in sorted(by_category.items())
            ])
            summary_parts.append(f"按类别: {category_text}")

        return "\n".join(summary_parts)


# 便捷函数
def validate_chapter_coherence(
    chapter_content: str,
    chapter_num: int,
    chapter_outline: str,
    character_tracker: CharacterTracker,
    plot_manager: PlotManager,
    world_db: WorldDatabase,
    api_client
) -> ValidationResult:
    """
    便捷函数：验证章节连贯性

    Args:
        chapter_content: 章节内容
        chapter_num: 章节号
        chapter_outline: 章节大纲
        character_tracker: 角色跟踪器
        plot_manager: 剧情管理器
        world_db: 世界观数据库
        api_client: API客户端

    Returns:
        ValidationResult对象
    """
    validator = CoherenceValidator(
        character_tracker,
        plot_manager,
        world_db,
        api_client
    )

    return validator.validate_chapter(
        chapter_content,
        chapter_num,
        chapter_outline
    )
