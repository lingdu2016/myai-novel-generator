"""
分层摘要管理器 - 解决长小说上下文断裂问题

核心思想：
- 将小说按卷划分（默认10章一卷）
- 每卷生成一个摘要（约500字）
- 保留最近N章的完整内容
- 生成章节时组合所有卷摘要 + 最近章节

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import json
import logging
from pathlib import Path
from ...config.paths import get_cache_dir
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class HierarchicalSummaryManager:
    """
    管理小说的分层摘要系统
    
    解决问题：当小说超过N章时，早期章节被完全丢弃，导致伏笔遗忘、角色设定丢失
    
    方案：
    - 第1-10章 → 第一卷摘要（500字）
    - 第11-20章 → 第二卷摘要（500字）
    - ...
    - 最新5章 → 完整内容
    """
    
    def __init__(
        self,
        project_id: str,
        chapters_per_arc: int = 10,
        recent_chapters: int = 5,
        cache_dir: Optional[Path] = None
    ):
        """
        初始化分层摘要管理器
        
        Args:
            project_id: 项目ID
            chapters_per_arc: 每卷章节数（默认10章一卷）
            recent_chapters: 保留完整内容的最近章节数（默认5章）
            cache_dir: 缓存目录
        """
        self.project_id = project_id
        self.chapters_per_arc = chapters_per_arc
        self.recent_chapters = recent_chapters
        self.cache_dir = cache_dir or get_cache_dir() / "coherence"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 卷摘要存储 {arc_id: {chapters, summary, main_events, character_changes, foreshadowing}}
        self.arc_summaries: Dict[int, Dict] = {}
        
        # 加载已有摘要
        self._load_summaries()
    
    def _get_summary_file(self) -> Path:
        """获取摘要文件路径"""
        return self.cache_dir / f"{self.project_id}_arc_summaries.json"
    
    def _load_summaries(self) -> None:
        """从文件加载卷摘要"""
        summary_file = self._get_summary_file()
        if not summary_file.exists():
            logger.info(f"未找到已有卷摘要文件: {summary_file}")
            return
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换key为整数
        for arc_key, arc_data in data.items():
            if arc_key.startswith("arc_"):
                arc_id = int(arc_key.replace("arc_", ""))
                self.arc_summaries[arc_id] = arc_data
        
        logger.info(f"已加载 {len(self.arc_summaries)} 个卷摘要")
    
    def _save_summaries(self) -> None:
        """保存卷摘要到文件"""
        summary_file = self._get_summary_file()
        
        # 转换为存储格式
        data = {}
        for arc_id, arc_data in self.arc_summaries.items():
            data[f"arc_{arc_id}"] = arc_data
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已保存 {len(self.arc_summaries)} 个卷摘要到 {summary_file}")
    
    def get_arc_id(self, chapter_num: int) -> int:
        """
        计算章节所属的卷号
        
        Args:
            chapter_num: 章节号（从1开始）
            
        Returns:
            卷号（从1开始）
        """
        # 第1-10章 → 卷1，第11-20章 → 卷2
        return (chapter_num - 1) // self.chapters_per_arc + 1
    
    def get_context_for_chapter(
        self,
        chapter_num: int,
        all_chapters: List[Dict],
        prev_chapter_tail_chars: int = 800
    ) -> str:
        """
        获取生成指定章节所需的上下文
        
        参数：
            chapter_num: 当前章节号（从1开始）
            all_chapters: 所有已有章节的列表 [{num, title, content, summary}, ...]
            prev_chapter_tail_chars: 前一章尾部字符数
            
        返回：
            构建好的上下文字符串
        """
        if not all_chapters:
            return "【这是第一章，直接开始创作】"
        
        context_parts = []
        current_arc = self.get_arc_id(chapter_num)
        
        # ========== 1. 添加之前所有卷的摘要 ==========
        if current_arc > 1:
            context_parts.append("【前文总览】")
            for arc_id in range(1, current_arc):
                arc_data = self.arc_summaries.get(arc_id)
                if arc_data and arc_data.get("summary"):
                    chapters_range = f"第{(arc_id-1)*self.chapters_per_arc + 1}-{arc_id*self.chapters_per_arc}章"
                    context_parts.append(f"\n【{chapters_range} 摘要】")
                    context_parts.append(arc_data["summary"])
                    
                    # 添加主要事件
                    if arc_data.get("main_events"):
                        context_parts.append("\n主要事件：")
                        for event in arc_data["main_events"]:
                            context_parts.append(f"- {event}")
                    
                    # 添加角色变化
                    if arc_data.get("character_changes"):
                        context_parts.append("\n角色变化：")
                        for change in arc_data["character_changes"]:
                            context_parts.append(f"- {change}")
                    
                    # 添加伏笔
                    if arc_data.get("foreshadowing"):
                        context_parts.append("\n伏笔：")
                        for foreshadow in arc_data["foreshadowing"]:
                            context_parts.append(f"- {foreshadow}")
            
            if len(context_parts) > 1:
                context_parts.append("")  # 空行分隔
                logger.info(f"已添加 {current_arc - 1} 个卷的摘要")
        
        # ========== 2. 添加当前卷的章节摘要（如果有） ==========
        current_arc_start = (current_arc - 1) * self.chapters_per_arc + 1
        current_arc_chapters = [
            ch for ch in all_chapters
            if current_arc_start <= ch.get("num", 0) < chapter_num
        ]
        
        if current_arc_chapters:
            context_parts.append(f"【本卷内容（第{current_arc_start}章起）】")
            for ch in current_arc_chapters:
                summary = ch.get("summary", "")
                title = ch.get("title", "")
                if summary:
                    context_parts.append(f"第{ch['num']}章《{title}》: {summary}")
                elif title:
                    context_parts.append(f"第{ch['num']}章《{title}》")
            context_parts.append("")
        
        # ========== 3. 添加最近N章的完整内容 ==========
        recent_start = max(1, chapter_num - self.recent_chapters)
        recent_chapters_list = [
            ch for ch in all_chapters
            if recent_start <= ch.get("num", 0) < chapter_num
        ]
        
        # 按章节号排序（从早到晚）
        recent_chapters_list.sort(key=lambda x: x.get("num", 0))
        
        if recent_chapters_list:
            context_parts.append(f"【最近{len(recent_chapters_list)}章详细内容】")
        
        for ch in recent_chapters_list:
            content = ch.get("content", "")
            title = ch.get("title", "")
            summary = ch.get("summary", "")
            
            if content and len(content) > 100:
                # 有完整内容，使用内容
                context_parts.append(f"\n第{ch['num']}章《{title}》:")
                context_parts.append(content)
            elif summary:
                # 只有摘要
                context_parts.append(f"\n第{ch['num']}章《{title}》摘要: {summary}")
            elif title:
                # 只有标题
                context_parts.append(f"\n第{ch['num']}章《{title}》")
        
        # ========== 4. 添加前一章尾部原文（确保无缝衔接） ==========
        if all_chapters and chapter_num > 1:
            # 获取紧邻的前一章
            prev_chapter = None
            for ch in reversed(all_chapters):
                if ch.get("num") == chapter_num - 1:
                    prev_chapter = ch
                    break
            
            if prev_chapter:
                prev_content = prev_chapter.get("content", "")
                if prev_content and len(prev_content) > 100:
                    tail_length = min(prev_chapter_tail_chars, len(prev_content))
                    chapter_tail = prev_content[-tail_length:]
                    
                    context_parts.append("")
                    context_parts.append("【前文结尾】")
                    context_parts.append(f"以下是第{prev_chapter['num']}章《{prev_chapter.get('title', '')}》的最后部分，请从这里自然衔接：")
                    context_parts.append("..." + chapter_tail)
                    logger.info(f"已加入前一章尾部原文: {tail_length} 字符")
        
        context_text = "\n".join(context_parts)
        logger.info(f"第{chapter_num}章上下文构建完成: 包含{current_arc - 1}个卷摘要, {len(current_arc_chapters)}章本卷摘要, {len(recent_chapters_list)}章详细内容")
        
        return context_text
    
    def update_arc_summary(
        self,
        arc_id: int,
        chapters: List[Dict],
        summary: str,
        main_events: Optional[List[str]] = None,
        character_changes: Optional[List[str]] = None,
        foreshadowing: Optional[List[str]] = None
    ) -> None:
        """
        更新指定卷的摘要
        
        Args:
            arc_id: 卷号
            chapters: 该卷的所有章节
            summary: 摘要文本
            main_events: 主要事件列表
            character_changes: 角色变化列表
            foreshadowing: 伏笔列表
        """
        chapter_nums = sorted([ch.get("num", 0) for ch in chapters])
        
        self.arc_summaries[arc_id] = {
            "chapters": chapter_nums,
            "summary": summary,
            "main_events": main_events or [],
            "character_changes": character_changes or [],
            "foreshadowing": foreshadowing or []
        }
        
        self._save_summaries()
        logger.info(f"已更新第{arc_id}卷摘要，包含章节: {chapter_nums}")
    
    def should_generate_arc_summary(self, chapter_num: int) -> bool:
        """
        判断是否需要生成新的卷摘要
        
        当一章是一卷的最后一章时（如第10章、第20章），需要生成卷摘要
        
        Args:
            chapter_num: 章节号
            
        Returns:
            是否需要生成卷摘要
        """
        return chapter_num > 0 and chapter_num % self.chapters_per_arc == 0
    
    def get_arc_chapters(self, arc_id: int, all_chapters: List[Dict]) -> List[Dict]:
        """
        获取指定卷的所有章节
        
        Args:
            arc_id: 卷号
            all_chapters: 所有章节列表
            
        Returns:
            该卷的章节列表
        """
        start_chapter = (arc_id - 1) * self.chapters_per_arc + 1
        end_chapter = arc_id * self.chapters_per_arc
        
        return [
            ch for ch in all_chapters
            if start_chapter <= ch.get("num", 0) <= end_chapter
        ]
    
    def get_summary_stats(self) -> Dict:
        """
        获取摘要系统统计信息
        
        Returns:
            统计信息字典
        """
        total_arcs = len(self.arc_summaries)
        total_chapters_covered = sum(
            len(arc_data.get("chapters", []))
            for arc_data in self.arc_summaries.values()
        )
        
        return {
            "total_arcs": total_arcs,
            "total_chapters_covered": total_chapters_covered,
            "chapters_per_arc": self.chapters_per_arc,
            "recent_chapters_kept": self.recent_chapters,
            "arc_summaries": list(self.arc_summaries.keys())
        }
    
    def clear_summaries(self) -> None:
        """清除所有卷摘要"""
        self.arc_summaries = {}
        summary_file = self._get_summary_file()
        if summary_file.exists():
            summary_file.unlink()
        logger.info(f"已清除项目 {self.project_id} 的所有卷摘要")