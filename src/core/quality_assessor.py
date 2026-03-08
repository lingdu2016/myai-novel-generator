"""
章节质量评估系统

核心功能：
1. 多维度质量评分
2. 连贯性检查
3. 情节完整性评估
4. 角色一致性检查
5. 文学性评估

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """质量维度"""
    COHERENCE = "连贯性"
    PLOT = "情节"
    CHARACTER = "角色"
    STYLE = "风格"
    READABILITY = "可读性"
    ORIGINALITY = "原创性"


@dataclass
class QualityScore:
    """质量分数"""
    dimension: QualityDimension
    score: float  # 0-100
    weight: float  # 权重
    issues: List[str]  # 问题列表
    suggestions: List[str]  # 改进建议


class QualityAssessor:
    """质量评估器"""

    def __init__(self, api_client=None):
        """
        初始化质量评估器

        Args:
            api_client: API客户端（可选）
        """
        self.api_client = api_client

        # 各维度权重
        self.dimension_weights = {
            QualityDimension.COHERENCE: 0.25,
            QualityDimension.PLOT: 0.20,
            QualityDimension.CHARACTER: 0.20,
            QualityDimension.STYLE: 0.15,
            QualityDimension.READABILITY: 0.10,
            QualityDimension.ORIGINALITY: 0.10,
        }

    def assess_chapter(
        self,
        content: str,
        chapter_num: int,
        chapter_outline: str = "",
        previous_summary: str = ""
    ) -> Dict:
        """
        评估章节质量

        Args:
            content: 章节内容
            chapter_num: 章节号
            chapter_outline: 章节大纲
            previous_summary: 前文摘要

        Returns:
            质量评估报告
        """
        logger.info(f"[质量评估] 开始评估第{chapter_num}章")

        scores = []

        # 1. 评估连贯性
        coherence_score = self._assess_coherence(content, previous_summary)
        scores.append(coherence_score)

        # 2. 评估情节
        plot_score = self._assess_plot(content, chapter_outline)
        scores.append(plot_score)

        # 3. 评估角色
        character_score = self._assess_character(content)
        scores.append(character_score)

        # 4. 评估风格
        style_score = self._assess_style(content)
        scores.append(style_score)

        # 5. 评估可读性
        readability_score = self._assess_readability(content)
        scores.append(readability_score)

        # 6. 评估原创性
        originality_score = self._assess_originality(content)
        scores.append(originality_score)

        # 计算总分
        total_score = self._calculate_total_score(scores)

        # 生成报告
        report = {
            "chapter_num": chapter_num,
            "total_score": total_score,
            "grade": self._get_grade(total_score),
            "dimension_scores": {
                score.dimension.value: {
                    "score": score.score,
                    "weight": score.weight,
                    "issues": score.issues,
                    "suggestions": score.suggestions
                }
                for score in scores
            },
            "overall_issues": self._collect_all_issues(scores),
            "overall_suggestions": self._collect_all_suggestions(scores),
        }

        logger.info(f"[质量评估] 第{chapter_num}章评估完成，总分: {total_score:.1f}")

        return report

    def _assess_coherence(
        self,
        content: str,
        previous_summary: str
    ) -> QualityScore:
        """评估连贯性"""
        issues = []
        suggestions = []
        score = 85.0  # 基础分

        # 检查段落衔接
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            transition_words = ['然而', '但是', '因此', '所以', '接着', '然后', '于是']
            smooth_transitions = 0

            for i in range(len(paragraphs) - 1):
                if any(word in paragraphs[i+1][:50] for word in transition_words):
                    smooth_transitions += 1

            transition_ratio = smooth_transitions / (len(paragraphs) - 1)
            if transition_ratio < 0.3:
                score -= 10
                issues.append("段落间衔接不自然")
                suggestions.append("增加过渡词或过渡句")

        # 检查时间线一致性
        time_indicators = ['早上', '中午', '下午', '晚上', '深夜', '第二天', '次日']
        time_mentions = [indicator for indicator in time_indicators if indicator in content]

        if len(time_mentions) > 3:
            # 检查时间顺序是否合理
            # 简化处理：如果有明显的时间跳跃需要说明
            score -= 5
            issues.append("时间线可能有跳跃")
            suggestions.append("确保时间变化有明确说明")

        # 检查场景一致性
        scene_keywords = ['房间里', '大街上', '森林里', '办公室']
        scene_changes = 0
        for keyword in scene_keywords:
            if keyword in content:
                scene_changes += 1

        if scene_changes > 2:
            score -= 5
            issues.append("场景变化较多，需要明确过渡")
            suggestions.append("增加场景转换的描述")

        return QualityScore(
            dimension=QualityDimension.COHERENCE,
            score=score,
            weight=self.dimension_weights[QualityDimension.COHERENCE],
            issues=issues,
            suggestions=suggestions
        )

    def _assess_plot(
        self,
        content: str,
        chapter_outline: str
    ) -> QualityScore:
        """评估情节"""
        issues = []
        suggestions = []
        score = 80.0  # 基础分

        # 检查情节推进
        action_verbs = ['冲', '跑', '跳', '打', '杀', '救', '逃', '追', '发现', '决定']
        action_count = sum(1 for verb in action_verbs if verb in content)

        if action_count < 3:
            score -= 15
            issues.append("情节推进缓慢，缺少行动")
            suggestions.append("增加角色行动或事件")

        # 检查冲突
        conflict_words = ['冲突', '矛盾', '争吵', '打斗', '对抗', '威胁']
        has_conflict = any(word in content for word in conflict_words)

        if not has_conflict:
            score -= 10
            issues.append("缺少冲突或矛盾")
            suggestions.append("增加角色间的冲突或矛盾")

        # 检查情节完整性
        if chapter_outline:
            # 检查是否覆盖了大纲要点
            outline_keywords = self._extract_keywords(chapter_outline)
            covered_keywords = [kw for kw in outline_keywords if kw in content]

            coverage_ratio = len(covered_keywords) / len(outline_keywords) if outline_keywords else 0
            if coverage_ratio < 0.5:
                score -= 10
                issues.append("未充分覆盖大纲要点")
                suggestions.append("确保覆盖大纲的主要内容")

        return QualityScore(
            dimension=QualityDimension.PLOT,
            score=score,
            weight=self.dimension_weights[QualityDimension.PLOT],
            issues=issues,
            suggestions=suggestions
        )

    def _assess_character(self, content: str) -> QualityScore:
        """评估角色"""
        issues = []
        suggestions = []
        score = 85.0  # 基础分

        # 检查角色出现
        # 简化处理：假设人名是2-4个汉字
        import re
        name_pattern = r'[\u4e00-\u9fa5]{2,4}'
        potential_names = set(re.findall(name_pattern, content))

        # 过滤掉常见非人名词汇
        common_words = {'突然', '竟然', '于是', '接着', '然后', '因此', '所以',
                       '因为', '由于', '虽然', '但是', '然而', '不过'}
        character_names = potential_names - common_words

        if len(character_names) < 2:
            score -= 10
            issues.append("角色数量较少")
            suggestions.append("增加角色互动")

        # 检查对话
        dialogue_pattern = r'"[^"]+"'
        dialogues = re.findall(dialogue_pattern, content)

        if len(dialogues) < 3:
            score -= 10
            issues.append("对话较少")
            suggestions.append("增加角色对话")

        # 检查角色行为一致性
        # 简化处理：检查是否有矛盾的行为描述
        # 这里需要更复杂的NLP处理，暂时跳过

        return QualityScore(
            dimension=QualityDimension.CHARACTER,
            score=score,
            weight=self.dimension_weights[QualityDimension.CHARACTER],
            issues=issues,
            suggestions=suggestions
        )

    def _assess_style(self, content: str) -> QualityScore:
        """评估风格"""
        issues = []
        suggestions = []
        score = 85.0  # 基础分

        # 检查AI味道
        from .style_optimizer import AITasteDetector
        detector = AITasteDetector()
        ai_issues = detector.detect_ai_taste(content)

        if ai_issues:
            high_severity = [i for i in ai_issues if i.severity == "high"]
            medium_severity = [i for i in ai_issues if i.severity == "medium"]

            if high_severity:
                score -= 20
                issues.extend([f"AI味道: {issue.text}" for issue in high_severity])
                suggestions.extend([issue.suggestion for issue in high_severity])

            if medium_severity:
                score -= 10
                issues.extend([f"AI味道: {issue.text}" for issue in medium_severity])
                suggestions.extend([issue.suggestion for issue in medium_severity])

        # 检查句式多样性
        sentences = content.split('。')
        sentence_lengths = [len(s.strip()) for s in sentences if s.strip()]

        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            if avg_length > 50:
                score -= 5
                issues.append("句子过长")
                suggestions.append("增加短句，调整节奏")

        # 检查描写具体性
        abstract_words = ['美丽', '壮观', '惊人', '震撼', '绝美', '惊艳']
        abstract_count = sum(1 for word in abstract_words if word in content)

        if abstract_count > 3:
            score -= 10
            issues.append("空洞形容词过多")
            suggestions.append("用具体细节代替空洞形容词")

        return QualityScore(
            dimension=QualityDimension.STYLE,
            score=score,
            weight=self.dimension_weights[QualityDimension.STYLE],
            issues=issues,
            suggestions=suggestions
        )

    def _assess_readability(self, content: str) -> QualityScore:
        """评估可读性"""
        issues = []
        suggestions = []
        score = 90.0  # 基础分

        # 检查句子长度
        sentences = content.split('。')
        long_sentences = [s for s in sentences if len(s.strip()) > 100]

        if len(long_sentences) > len(sentences) * 0.2:
            score -= 10
            issues.append("长句过多")
            suggestions.append("将长句拆分成短句")

        # 检查段落长度
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p.strip()) > 500]

        if len(long_paragraphs) > len(paragraphs) * 0.3:
            score -= 5
            issues.append("段落过长")
            suggestions.append("将长段落拆分")

        # 检查重复词汇
        words = content.split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        repeated_words = [word for word, freq in word_freq.items() if freq > 10]
        if repeated_words:
            score -= 5
            issues.append(f"词汇重复: {', '.join(repeated_words[:3])}")
            suggestions.append("使用同义词替换重复词汇")

        return QualityScore(
            dimension=QualityDimension.READABILITY,
            score=score,
            weight=self.dimension_weights[QualityDimension.READABILITY],
            issues=issues,
            suggestions=suggestions
        )

    def _assess_originality(self, content: str) -> QualityScore:
        """评估原创性"""
        issues = []
        suggestions = []
        score = 85.0  # 基础分

        # 检查陈词滥调
        cliches = [
            '一石二鸟', '一箭双雕', '千钧一发', '刻不容缓',
            '欣喜若狂', '悲痛欲绝', '怒发冲冠', '胆战心惊'
        ]

        cliches_found = [c for c in cliches if c in content]
        if cliches_found:
            score -= 10
            issues.append(f"使用陈词滥调: {', '.join(cliches_found)}")
            suggestions.append("用原创表达替换陈词滥调")

        # 检查情节套路
        plot_tropes = [
            '英雄救美', '绝处逢生', '因祸得福', '死里逃生',
            '失忆', '穿越', '重生', '系统'
        ]

        tropes_found = [t for t in plot_tropes if t in content]
        if tropes_found:
            score -= 5
            issues.append(f"使用常见套路: {', '.join(tropes_found)}")
            suggestions.append("尝试创新情节设计")

        return QualityScore(
            dimension=QualityDimension.ORIGINALITY,
            score=score,
            weight=self.dimension_weights[QualityDimension.ORIGINALITY],
            issues=issues,
            suggestions=suggestions
        )

    def _calculate_total_score(self, scores: List[QualityScore]) -> float:
        """计算总分"""
        total = 0.0
        for score in scores:
            total += score.score * score.weight
        return round(total, 1)

    def _get_grade(self, score: float) -> str:
        """获取评级"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _collect_all_issues(self, scores: List[QualityScore]) -> List[str]:
        """收集所有问题"""
        all_issues = []
        for score in scores:
            all_issues.extend([f"[{score.dimension.value}] {issue}" for issue in score.issues])
        return all_issues

    def _collect_all_suggestions(self, scores: List[QualityScore]) -> List[str]:
        """收集所有建议"""
        all_suggestions = []
        for score in scores:
            all_suggestions.extend([f"[{score.dimension.value}] {suggestion}" for suggestion in score.suggestions])
        return all_suggestions

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        import re
        # 简化处理：提取2-4个字的词汇
        pattern = r'[\u4e00-\u9fa5]{2,4}'
        keywords = re.findall(pattern, text)

        # 过滤掉常见虚词
        stop_words = {'这个', '那个', '什么', '怎么', '为什么', '因为', '所以',
                       '但是', '然而', '于是', '接着', '然后', '因此'}
        keywords = [kw for kw in keywords if kw not in stop_words]

        return keywords


# 便捷函数
def assess_chapter_quality(
    content: str,
    chapter_num: int,
    chapter_outline: str = "",
    previous_summary: str = "",
    api_client=None
) -> Dict:
    """
    评估章节质量

    Args:
        content: 章节内容
        chapter_num: 章节号
        chapter_outline: 章节大纲
        previous_summary: 前文摘要
        api_client: API客户端（可选）

    Returns:
        质量评估报告
    """
    assessor = QualityAssessor(api_client)
    return assessor.assess_chapter(content, chapter_num, chapter_outline, previous_summary)
