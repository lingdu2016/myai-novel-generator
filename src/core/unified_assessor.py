"""
统一评估系统

整合AI去味和质量评估，提供统一的评估接口

核心功能：
1. 统一评分系统（AI去味 + 质量评估）
2. AI去味等级设置（基础/强力）
3. 质量评估开关和重写阈值
4. 详细的评估报告输出

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

from .style_optimizer import AITasteDetector, AITasteCorrector, StyleOptimizer
from .quality_assessor import QualityAssessor, QualityDimension

logger = logging.getLogger(__name__)


class AITasteLevel(Enum):
    """AI去味等级"""
    DISABLED = "disabled"  # 禁用
    BASIC = "basic"  # 基础去味
    STRONG = "strong"  # 强力去味


@dataclass
class AssessmentIssue:
    """评估问题"""
    category: str  # 问题类别：ai_taste / quality
    dimension: str  # 维度：forbidden_word / coherence / plot / ...
    severity: str  # 严重程度：low / medium / high
    description: str  # 问题描述
    position: Optional[int] = None  # 位置（可选）
    text: Optional[str] = None  # 问题文本（可选）
    suggestion: str = ""  # 修改建议


@dataclass
class AssessmentReport:
    """统一评估报告"""
    # 总分
    total_score: float = 0.0
    grade: str = "D"
    
    # AI去味评分
    ai_taste_score: float = 0.0
    ai_taste_grade: str = "D"
    ai_taste_issues: List[AssessmentIssue] = field(default_factory=list)
    
    # 质量评分
    quality_score: float = 0.0
    quality_grade: str = "D"
    quality_issues: List[AssessmentIssue] = field(default_factory=list)
    
    # 各维度评分
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    
    # 是否需要重写
    need_rewrite: bool = False
    rewrite_reason: str = ""
    
    # 优化后的内容
    optimized_content: Optional[str] = None
    
    # 详细报告文本
    detailed_report: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "total_score": self.total_score,
            "grade": self.grade,
            "ai_taste_score": self.ai_taste_score,
            "ai_taste_grade": self.ai_taste_grade,
            "quality_score": self.quality_score,
            "quality_grade": self.quality_grade,
            "dimension_scores": self.dimension_scores,
            "need_rewrite": self.need_rewrite,
            "rewrite_reason": self.rewrite_reason,
            "detailed_report": self.detailed_report,
            "ai_taste_issues_count": len(self.ai_taste_issues),
            "quality_issues_count": len(self.quality_issues),
        }


class UnifiedAssessor:
    """统一评估器"""
    
    def __init__(self, api_client=None):
        """
        初始化统一评估器
        
        Args:
            api_client: API客户端
        """
        self.api_client = api_client
        
        # 初始化子系统
        self.ai_detector = AITasteDetector()
        self.ai_corrector = AITasteCorrector()
        self.style_optimizer = StyleOptimizer(api_client)
        self.quality_assessor = QualityAssessor(api_client)
        
        # 评估配置
        self.config = {
            # AI去味配置
            "ai_taste_level": AITasteLevel.BASIC,  # 默认基础去味
            "ai_taste_weight": 0.4,  # AI去味权重
            
            # 质量评估配置
            "enable_quality_assessment": True,  # 启用质量评估
            "quality_weight": 0.6,  # 质量评估权重
            "quality_min_score": 70.0,  # 最低质量分
            "quality_rewrite_threshold": 60.0,  # 重写阈值
            
            # 总分配置
            "total_min_score": 65.0,  # 最低总分
            "total_rewrite_threshold": 55.0,  # 总分重写阈值
        }
    
    def configure(
        self,
        ai_taste_level: str = "basic",
        enable_quality_assessment: bool = True,
        quality_min_score: float = 70.0,
        quality_rewrite_threshold: float = 60.0,
        total_min_score: float = 65.0,
        total_rewrite_threshold: float = 55.0
    ):
        """
        配置评估参数
        
        Args:
            ai_taste_level: AI去味等级 (disabled/basic/strong)
            enable_quality_assessment: 是否启用质量评估
            quality_min_score: 最低质量分
            quality_rewrite_threshold: 质量重写阈值
            total_min_score: 最低总分
            total_rewrite_threshold: 总分重写阈值
        """
        # 设置AI去味等级
        if ai_taste_level == "disabled":
            self.config["ai_taste_level"] = AITasteLevel.DISABLED
        elif ai_taste_level == "basic":
            self.config["ai_taste_level"] = AITasteLevel.BASIC
        elif ai_taste_level == "strong":
            self.config["ai_taste_level"] = AITasteLevel.STRONG
        else:
            logger.warning(f"未知的AI去味等级: {ai_taste_level}，使用默认值basic")
            self.config["ai_taste_level"] = AITasteLevel.BASIC
        
        # 设置质量评估参数
        self.config["enable_quality_assessment"] = enable_quality_assessment
        self.config["quality_min_score"] = quality_min_score
        self.config["quality_rewrite_threshold"] = quality_rewrite_threshold
        self.config["total_min_score"] = total_min_score
        self.config["total_rewrite_threshold"] = total_rewrite_threshold
        
        logger.info(f"[统一评估] 配置更新: AI去味={ai_taste_level}, 质量评估={enable_quality_assessment}")
        logger.info(f"[统一评估] 阈值设置: 质量最低={quality_min_score}, 质量重写={quality_rewrite_threshold}")
        logger.info(f"[统一评估] 阈值设置: 总分最低={total_min_score}, 总分重写={total_rewrite_threshold}")
    
    def assess(
        self,
        content: str,
        chapter_num: int,
        chapter_outline: str = "",
        previous_summary: str = "",
        optimize: bool = True
    ) -> AssessmentReport:
        """
        统一评估章节
        
        Args:
            content: 章节内容
            chapter_num: 章节号
            chapter_outline: 章节大纲
            previous_summary: 前文摘要
            optimize: 是否进行优化
            
        Returns:
            评估报告
        """
        logger.info(f"[统一评估] 开始评估第{chapter_num}章")
        
        report = AssessmentReport()
        current_content = content
        
        # ========== 1. AI去味评估 ==========
        if self.config["ai_taste_level"] != AITasteLevel.DISABLED:
            ai_score, ai_grade, ai_issues = self._assess_ai_taste(
                current_content,
                chapter_num
            )
            
            report.ai_taste_score = ai_score
            report.ai_taste_grade = ai_grade
            report.ai_taste_issues = ai_issues
            
            # 如果启用优化，进行AI去味
            if optimize and self.config["ai_taste_level"] != AITasteLevel.DISABLED:
                current_content = self._optimize_ai_taste(
                    current_content,
                    chapter_num,
                    ai_score,
                    ai_issues
                )
                report.optimized_content = current_content
        
        # ========== 2. 质量评估 ==========
        if self.config["enable_quality_assessment"]:
            quality_score, quality_grade, quality_issues, dimension_scores = self._assess_quality(
                current_content,
                chapter_num,
                chapter_outline,
                previous_summary
            )
            
            report.quality_score = quality_score
            report.quality_grade = quality_grade
            report.quality_issues = quality_issues
            report.dimension_scores = dimension_scores
        
        # ========== 3. 计算总分 ==========
        report.total_score, report.grade = self._calculate_total_score(report)
        
        # ========== 4. 判断是否需要重写 ==========
        report.need_rewrite, report.rewrite_reason = self._check_need_rewrite(report)
        
        # ========== 5. 生成详细报告 ==========
        report.detailed_report = self._generate_detailed_report(report, chapter_num)
        
        logger.info(f"[统一评估] 第{chapter_num}章评估完成: 总分={report.total_score:.1f} ({report.grade})")
        
        return report
    
    def _assess_ai_taste(
        self,
        content: str,
        chapter_num: int
    ) -> Tuple[float, str, List[AssessmentIssue]]:
        """
        评估AI味道
        
        Args:
            content: 章节内容
            chapter_num: 章节号
            
        Returns:
            (分数, 等级, 问题列表)
        """
        logger.info(f"[AI去味评估] 开始检测第{chapter_num}章")
        
        # 检测AI味道
        style_issues = self.ai_detector.detect_ai_taste(content)
        
        # 转换为统一的问题格式
        issues = []
        for issue in style_issues:
            issues.append(AssessmentIssue(
                category="ai_taste",
                dimension=issue.issue_type,
                severity=issue.severity,
                description=f"发现AI化表达: {issue.text}",
                position=issue.position,
                text=issue.text,
                suggestion=issue.suggestion
            ))
        
        # 计算分数
        score, grade = self.ai_corrector.get_quality_score(content)
        
        # 统计问题
        high_count = sum(1 for i in issues if i.severity == "high")
        medium_count = sum(1 for i in issues if i.severity == "medium")
        low_count = sum(1 for i in issues if i.severity == "low")
        
        logger.info(f"[AI去味评估] 检测到 {len(issues)} 个问题: 高={high_count}, 中={medium_count}, 低={low_count}")
        logger.info(f"[AI去味评估] 得分: {score:.1f} ({grade})")
        
        return score, grade, issues
    
    def _optimize_ai_taste(
        self,
        content: str,
        chapter_num: int,
        current_score: float,
        issues: List[AssessmentIssue]
    ) -> str:
        """
        优化AI味道
        
        Args:
            content: 章节内容
            chapter_num: 章节号
            current_score: 当前分数
            issues: 问题列表
            
        Returns:
            优化后的内容
        """
        level = self.config["ai_taste_level"]
        
        if level == AITasteLevel.DISABLED:
            return content
        
        logger.info(f"[AI去味优化] 第{chapter_num}章，等级={level.value}, 当前分={current_score:.1f}")
        
        optimized_content = content
        
        # 基础去味：本地自动修正
        if level == AITasteLevel.BASIC:
            if current_score < 85:
                logger.info(f"[AI去味优化] 使用本地优化")
                optimized_content, _ = self.style_optimizer.optimize_chapter(
                    content,
                    auto_correct=True
                )
        
        # 强力去味：AI辅助优化
        elif level == AITasteLevel.STRONG:
            if current_score < 85:
                logger.info(f"[AI去味优化] 使用AI优化")
                try:
                    optimized_content, _ = self.style_optimizer.optimize_with_ai(content)
                except Exception as e:
                    logger.warning(f"[AI去味优化] AI优化失败: {e}，回退到本地优化")
                    optimized_content, _ = self.style_optimizer.optimize_chapter(
                        content,
                        auto_correct=True
                    )
        
        # 重新评估优化后的内容
        if optimized_content != content:
            new_score, new_grade = self.ai_corrector.get_quality_score(optimized_content)
            logger.info(f"[AI去味优化] 优化完成: {current_score:.1f} -> {new_score:.1f}")
        
        return optimized_content
    
    def _assess_quality(
        self,
        content: str,
        chapter_num: int,
        chapter_outline: str,
        previous_summary: str
    ) -> Tuple[float, str, List[AssessmentIssue], Dict[str, float]]:
        """
        评估质量
        
        Args:
            content: 章节内容
            chapter_num: 章节号
            chapter_outline: 章节大纲
            previous_summary: 前文摘要
            
        Returns:
            (分数, 等级, 问题列表, 维度分数)
        """
        logger.info(f"[质量评估] 开始评估第{chapter_num}章")
        
        # 使用质量评估器
        quality_report = self.quality_assessor.assess_chapter(
            content=content,
            chapter_num=chapter_num,
            chapter_outline=chapter_outline,
            previous_summary=previous_summary
        )
        
        # 提取分数
        total_score = quality_report.get("total_score", 0)
        
        # 提取维度分数
        dimension_scores = {}
        for dim_name, dim_data in quality_report.get("dimensions", {}).items():
            dimension_scores[dim_name] = dim_data.get("score", 0)
        
        # 提取问题
        issues = []
        for dim_name, dim_data in quality_report.get("dimensions", {}).items():
            for problem in dim_data.get("problems", []):
                issues.append(AssessmentIssue(
                    category="quality",
                    dimension=dim_name,
                    severity="medium",  # 默认中等严重程度
                    description=problem,
                    suggestion=dim_data.get("suggestions", [""])[0] if dim_data.get("suggestions") else ""
                ))
        
        # 计算等级
        if total_score >= 90:
            grade = "A"
        elif total_score >= 80:
            grade = "B"
        elif total_score >= 70:
            grade = "C"
        elif total_score >= 60:
            grade = "D"
        else:
            grade = "E"
        
        logger.info(f"[质量评估] 得分: {total_score:.1f} ({grade})")
        
        return total_score, grade, issues, dimension_scores
    
    def _calculate_total_score(self, report: AssessmentReport) -> Tuple[float, str]:
        """
        计算总分
        
        Args:
            report: 评估报告
            
        Returns:
            (总分, 等级)
        """
        ai_weight = self.config["ai_taste_weight"]
        quality_weight = self.config["quality_weight"]
        
        # 如果禁用了AI去味，只看质量分
        if self.config["ai_taste_level"] == AITasteLevel.DISABLED:
            total_score = report.quality_score
        # 如果禁用了质量评估，只看AI去味分
        elif not self.config["enable_quality_assessment"]:
            total_score = report.ai_taste_score
        # 否则按权重计算
        else:
            total_score = (
                report.ai_taste_score * ai_weight +
                report.quality_score * quality_weight
            )
        
        # 计算等级
        if total_score >= 90:
            grade = "A"
        elif total_score >= 80:
            grade = "B"
        elif total_score >= 70:
            grade = "C"
        elif total_score >= 60:
            grade = "D"
        else:
            grade = "E"
        
        return total_score, grade
    
    def _check_need_rewrite(self, report: AssessmentReport) -> Tuple[bool, str]:
        """
        检查是否需要重写
        
        Args:
            report: 评估报告
            
        Returns:
            (是否需要重写, 原因)
        """
        reasons = []
        
        # 检查总分
        if report.total_score < self.config["total_rewrite_threshold"]:
            reasons.append(f"总分过低 ({report.total_score:.1f} < {self.config['total_rewrite_threshold']})")
        
        # 检查质量分
        if self.config["enable_quality_assessment"]:
            if report.quality_score < self.config["quality_rewrite_threshold"]:
                reasons.append(f"质量分过低 ({report.quality_score:.1f} < {self.config['quality_rewrite_threshold']})")
        
        # 检查AI去味分
        if self.config["ai_taste_level"] != AITasteLevel.DISABLED:
            if report.ai_taste_score < 50:
                reasons.append(f"AI味道过重 ({report.ai_taste_score:.1f} < 50)")
        
        need_rewrite = len(reasons) > 0
        reason = "; ".join(reasons) if reasons else ""
        
        if need_rewrite:
            logger.warning(f"[重写判断] 需要重写: {reason}")
        
        return need_rewrite, reason
    
    def _generate_detailed_report(self, report: AssessmentReport, chapter_num: int) -> str:
        """
        生成详细报告
        
        Args:
            report: 评估报告
            chapter_num: 章节号
            
        Returns:
            详细报告文本
        """
        lines = []
        lines.append(f"=" * 60)
        lines.append(f"第{chapter_num}章 统一评估报告")
        lines.append(f"=" * 60)
        lines.append("")
        
        # 总分
        lines.append(f"【总分】 {report.total_score:.1f} 分 ({report.grade})")
        lines.append("")
        
        # AI去味评分
        if self.config["ai_taste_level"] != AITasteLevel.DISABLED:
            lines.append(f"【AI去味评分】 {report.ai_taste_score:.1f} 分 ({report.ai_taste_grade})")
            if report.ai_taste_issues:
                lines.append(f"  发现 {len(report.ai_taste_issues)} 个问题:")
                for i, issue in enumerate(report.ai_taste_issues[:10], 1):  # 只显示前10个
                    lines.append(f"    {i}. [{issue.severity}] {issue.description}")
                    if issue.suggestion:
                        lines.append(f"       建议: {issue.suggestion}")
            lines.append("")
        
        # 质量评分
        if self.config["enable_quality_assessment"]:
            lines.append(f"【质量评分】 {report.quality_score:.1f} 分 ({report.quality_grade})")
            if report.dimension_scores:
                lines.append(f"  各维度评分:")
                for dim, score in report.dimension_scores.items():
                    lines.append(f"    - {dim}: {score:.1f} 分")
            if report.quality_issues:
                lines.append(f"  发现 {len(report.quality_issues)} 个问题:")
                for i, issue in enumerate(report.quality_issues[:10], 1):  # 只显示前10个
                    lines.append(f"    {i}. [{issue.dimension}] {issue.description}")
                    if issue.suggestion:
                        lines.append(f"       建议: {issue.suggestion}")
            lines.append("")
        
        # 重写建议
        if report.need_rewrite:
            lines.append(f"【重写建议】")
            lines.append(f"  ⚠️ 建议重写本章")
            lines.append(f"  原因: {report.rewrite_reason}")
        else:
            lines.append(f"【重写建议】")
            lines.append(f"  ✅ 质量合格，无需重写")
        
        lines.append("")
        lines.append(f"=" * 60)
        
        return "\n".join(lines)


def create_assessment_prompt(report: AssessmentReport) -> str:
    """
    根据评估报告创建重写提示词
    
    Args:
        report: 评估报告
        
    Returns:
        重写提示词
    """
    prompt_parts = []
    
    prompt_parts.append("【上一版问题总结】")
    prompt_parts.append("")
    
    # AI去味问题
    if report.ai_taste_issues:
        prompt_parts.append("AI味道问题:")
        for i, issue in enumerate(report.ai_taste_issues[:5], 1):
            prompt_parts.append(f"{i}. {issue.description}")
            if issue.suggestion:
                prompt_parts.append(f"   修改建议: {issue.suggestion}")
        prompt_parts.append("")
    
    # 质量问题
    if report.quality_issues:
        prompt_parts.append("质量问题:")
        for i, issue in enumerate(report.quality_issues[:5], 1):
            prompt_parts.append(f"{i}. [{issue.dimension}] {issue.description}")
            if issue.suggestion:
                prompt_parts.append(f"   修改建议: {issue.suggestion}")
        prompt_parts.append("")
    
    # 总体建议
    prompt_parts.append("【改进要求】")
    prompt_parts.append(f"上一版总分: {report.total_score:.1f} 分")
    prompt_parts.append(f"上一版问题: {report.rewrite_reason}")
    prompt_parts.append("")
    prompt_parts.append("请根据以上问题重新创作本章，注意:")
    prompt_parts.append("1. 避免使用AI化表达")
    prompt_parts.append("2. 提高情节连贯性")
    prompt_parts.append("3. 增强角色刻画")
    prompt_parts.append("4. 丰富细节描写")
    prompt_parts.append("5. 保持风格一致")
    
    return "\n".join(prompt_parts)
