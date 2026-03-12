"""
角色状态跟踪系统 - 追踪角色在各章节中的状态、性格、关系变化

优化：增加 next_chapter_note 功能，为下一章创作提供指导

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import json
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from ...config.paths import get_cache_dir

logger = logging.getLogger(__name__)


@dataclass
class CharacterState:
    """角色在某一时刻的状态"""
    name: str                          # 角色名称
    personality: str                   # 性格特征
    mood: str = ""                     # 当前情绪
    location: str = ""                 # 当前位置
    relationships: Dict[str, str] = field(default_factory=dict)  # 人际关系 {角色名: 关系描述}
    goals: List[str] = field(default_factory=list)  # 当前目标
    backstory: str = ""                # 背景故事
    arc_stage: str = ""                # 角色弧光阶段 (introduction/rising/climax/resolution)
    chapter_num: int = 0               # 记录时的章节号
    next_chapter_note: str = ""        # 下一章需要注意的事项（新增）
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CharacterState':
        """从字典创建"""
        return cls(**data)


@dataclass
class CharacterEvent:
    """角色相关事件"""
    chapter_num: int                   # 发生章节
    event_type: str                    # 事件类型 (appearance/state_change/interaction/departure)
    description: str                   # 事件描述
    context: str = ""                  # 上下文信息
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class CharacterTracker:
    """
    角色状态跟踪器

    功能：
    1. 记录每个角色在各章节中的状态
    2. 追踪角色状态变化
    3. 检测角色行为的一致性
    4. 提供角色历史查询
    """

    def __init__(self, project_id: str, cache_dir: Optional[Path] = None):
        """
        初始化角色跟踪器

        Args:
            project_id: 项目ID
            cache_dir: 缓存目录
        """
        self.project_id = project_id
        self.cache_dir = cache_dir or get_cache_dir() / "coherence"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 角色状态历史 {character_name: [CharacterState]}
        self.character_history: Dict[str, List[CharacterState]] = {}

        # 角色事件 {character_name: [CharacterEvent]}
        self.character_events: Dict[str, List[CharacterEvent]] = {}

        # 所有出现过的角色
        self.all_characters: Set[str] = set()

        # 归档的角色档案 {character_name: {state, relationships, key_events, last_chapter}}
        self.archived_profiles: Dict[str, Dict] = {}

        # 记录更新的次数，用于触发自动归档
        self._update_count: int = 0

        # 加载已有数据
        self._load_from_disk()

    def track_character_appearance(
        self,
        chapter_num: int,
        character_name: str,
        context: str,
        personality_hint: Optional[str] = None
    ) -> None:
        """
        记录角色出现

        Args:
            chapter_num: 章节号
            character_name: 角色名
            context: 上下文（该角色在本章的描述）
            personality_hint: 性格提示（如果是首次出现）
        """
        self.all_characters.add(character_name)

        # 创建事件
        event = CharacterEvent(
            chapter_num=chapter_num,
            event_type="appearance",
            description=f"角色 {character_name} 出现在第{chapter_num}章",
            context=context
        )

        if character_name not in self.character_events:
            self.character_events[character_name] = []
        self.character_events[character_name].append(event)

        # 如果是首次出现且有性格提示，记录初始状态
        if character_name not in self.character_history and personality_hint:
            initial_state = CharacterState(
                name=character_name,
                personality=personality_hint,
                chapter_num=chapter_num
            )
            self.character_history[character_name] = [initial_state]

        logger.info(f"记录角色出现: {character_name} 在第{chapter_num}章")

    def update_character_state(
        self,
        chapter_num: int,
        character_name: str,
        updates: Dict[str, any]
    ) -> None:
        """
        更新角色状态

        Args:
            chapter_num: 章节号
            character_name: 角色名
            updates: 更新的字段 {mood: "...", location: "...", etc.}
        """
        if character_name not in self.character_history:
            logger.warning(f"角色 {character_name} 尚未初始化，先记录其出现")
            self.track_character_appearance(chapter_num, character_name, "")

        # 获取最新状态
        latest_state = self.character_history[character_name][-1]

        # 创建新状态
        new_state = CharacterState(
            name=character_name,
            personality=latest_state.personality,
            chapter_num=chapter_num
        )

        # 应用更新
        for key, value in updates.items():
            if hasattr(new_state, key):
                setattr(new_state, key, value)
            else:
                logger.warning(f"CharacterState 没有字段: {key}")

        # 记录事件
        event = CharacterEvent(
            chapter_num=chapter_num,
            event_type="state_change",
            description=f"角色 {character_name} 状态更新",
            context=json.dumps(updates, ensure_ascii=False)
        )
        self.character_events[character_name].append(event)

        # 保存新状态
        self.character_history[character_name].append(new_state)

        # 更新计数并检查是否需要自动归档
        self._update_count += 1
        if self._update_count % 100 == 0:
            self.archive_old_records(keep_recent=50)

        logger.info(f"更新角色状态: {character_name} 在第{chapter_num}章")

    def track_relationship_change(
        self,
        chapter_num: int,
        character_name: str,
        other_character: str,
        relationship: str
    ) -> None:
        """
        追踪角色关系变化

        Args:
            chapter_num: 章节号
            character_name: 角色1
            other_character: 角色2
            relationship: 关系描述
        """
        if character_name not in self.character_history:
            self.track_character_appearance(chapter_num, character_name, "")

        # 获取最新状态并更新关系
        latest_state = self.character_history[character_name][-1]
        new_relationships = latest_state.relationships.copy()
        new_relationships[other_character] = relationship

        # 更新状态
        self.update_character_state(
            chapter_num,
            character_name,
            {"relationships": new_relationships}
        )

        # 记录事件
        event = CharacterEvent(
            chapter_num=chapter_num,
            event_type="relationship_change",
            description=f"{character_name} 与 {other_character} 的关系变为: {relationship}",
            context=""
        )
        self.character_events[character_name].append(event)

        logger.info(f"更新关系: {character_name} - {other_character}: {relationship}")

    def get_character_history(self, character_name: str) -> List[CharacterState]:
        """
        获取角色的完整历史状态

        Args:
            character_name: 角色名

        Returns:
            状态列表（按时间排序）
        """
        return self.character_history.get(character_name, [])

    def get_character_current_state(self, character_name: str) -> Optional[CharacterState]:
        """
        获取角色最新状态

        Args:
            character_name: 角色名

        Returns:
            最新状态，如果角色不存在则返回None
        """
        history = self.character_history.get(character_name)
        return history[-1] if history else None

    def archive_old_records(self, keep_recent: int = 50) -> None:
        """
        归档旧记录，只保留最近N条详细记录

        Args:
            keep_recent: 每个角色保留的最近记录数
        """
        total_archived = 0

        for char_name, history in self.character_history.items():
            if len(history) <= keep_recent:
                continue

            # 分离近期记录和旧记录
            old_records = history[:-keep_recent]
            recent_records = history[-keep_recent:]

            # 将旧记录压缩为角色档案摘要
            archived_profile = self._create_archived_profile(char_name, old_records)

            # 合并到已有的归档档案中
            if char_name in self.archived_profiles:
                existing = self.archived_profiles[char_name]
                # 更新状态
                existing['state'].update(archived_profile['state'])
                existing['relationships'].update(archived_profile['relationships'])
                # 合并关键事件（去重）
                for event in archived_profile['key_events']:
                    if event not in existing['key_events']:
                        existing['key_events'].append(event)
                existing['last_chapter'] = archived_profile['last_chapter']
            else:
                self.archived_profiles[char_name] = archived_profile

            # 更新历史记录为只保留近期
            self.character_history[char_name] = recent_records
            total_archived += len(old_records)

        if total_archived > 0:
            logger.info(f"归档完成: 共归档 {total_archived} 条旧记录")
            self.save_to_disk()

    def _create_archived_profile(self, char_name: str, old_records: List[CharacterState]) -> Dict:
        """
        从旧记录创建归档档案

        Args:
            char_name: 角色名
            old_records: 旧记录列表

        Returns:
            归档档案字典
        """
        profile = {
            'name': char_name,
            'state': {},
            'relationships': {},
            'key_events': [],
            'last_chapter': 0
        }

        for record in old_records:
            # 更新状态（后记录覆盖前记录）
            profile['state']['personality'] = record.personality
            if record.mood:
                profile['state']['mood'] = record.mood
            if record.location:
                profile['state']['location'] = record.location
            if record.goals:
                profile['state']['goals'] = record.goals
            if record.backstory:
                profile['state']['backstory'] = record.backstory
            if record.arc_stage:
                profile['state']['arc_stage'] = record.arc_stage

            # 更新关系
            profile['relationships'].update(record.relationships)

            # 更新最后章节号
            profile['last_chapter'] = max(profile['last_chapter'], record.chapter_num)

            # 记录关键事件（使用 next_chapter_note 作为事件标记）
            if record.next_chapter_note:
                event_desc = f"第{record.chapter_num}章: {record.next_chapter_note}"
                if event_desc not in profile['key_events']:
                    profile['key_events'].append(event_desc)

        return profile

    def get_character_info(self, character_name: str) -> Dict:
        """
        获取角色完整信息（包含归档数据）

        Args:
            character_name: 角色名

        Returns:
            角色完整信息字典
        """
        # 从归档获取基础信息
        info = self.archived_profiles.get(character_name, {}).copy()

        # 从当前记录更新最新状态
        history = self.character_history.get(character_name, [])
        if history:
            latest = history[-1]
            # 确保state字典存在
            if 'state' not in info:
                info['state'] = {}
            if 'relationships' not in info:
                info['relationships'] = {}

            # 更新最新状态
            info['state']['personality'] = latest.personality
            if latest.mood:
                info['state']['mood'] = latest.mood
            if latest.location:
                info['state']['location'] = latest.location
            if latest.goals:
                info['state']['goals'] = latest.goals
            if latest.backstory:
                info['state']['backstory'] = latest.backstory
            if latest.arc_stage:
                info['state']['arc_stage'] = latest.arc_stage

            info['relationships'].update(latest.relationships)
            info['last_chapter'] = latest.chapter_num
            info['name'] = character_name

        return info

    def get_characters_in_chapter(self, chapter_num: int) -> List[str]:
        """
        获取指定章节中出现的所有角色

        Args:
            chapter_num: 章节号

        Returns:
            角色名列表
        """
        characters = []
        for char_name, events in self.character_events.items():
            if any(e.chapter_num == chapter_num for e in events):
                characters.append(char_name)
        return characters

    def detect_inconsistencies(self) -> List[str]:
        """
        检测角色一致性问题

        Returns:
            问题列表
        """
        issues = []

        for char_name, history in self.character_history.items():
            if len(history) < 2:
                continue

            # 检查性格突变
            for i in range(1, len(history)):
                prev_state = history[i-1]
                curr_state = history[i]

                # 性格描述差异过大
                if self._is_personality_drastic_change(prev_state.personality, curr_state.personality):
                    issues.append(
                        f"角色 {char_name} 性格在第{curr_state.chapter_num}章发生突变: "
                        f"从 '{prev_state.personality}' 变为 '{curr_state.personality}'"
                    )

                # 位置不合理变化（没有过渡）
                if prev_state.location and curr_state.location:
                    if prev_state.location != curr_state.location:
                        # 检查是否有合理的过渡描述
                        has_transition = any(
                            e.event_type == "state_change" and
                            prev_state.chapter_num <= e.chapter_num <= curr_state.chapter_num
                            for e in self.character_events.get(char_name, [])
                        )
                        if not has_transition:
                            issues.append(
                                f"角色 {char_name} 位置在第{curr_state.chapter_num}章不合理变化: "
                                f"从 {prev_state.location} 瞬间到 {curr_state.location}"
                            )

        return issues

    def _is_personality_drastic_change(self, old: str, new: str) -> bool:
        """
        检查性格是否发生剧烈变化

        这是一个简化版本，实际应该使用AI语义分析
        """
        if not old or not new:
            return False

        # 简单的词汇重叠度检查
        old_words = set(old.split())
        new_words = set(new.split())

        overlap = len(old_words & new_words)
        total = len(old_words | new_words)

        # 如果重叠度低于30%，认为是剧烈变化
        return total > 0 and overlap / total < 0.3

    def get_character_summary_for_context(
        self,
        character_name: str,
        up_to_chapter: int
    ) -> str:
        """
        生成角色摘要，用于上下文生成

        Args:
            character_name: 角色名
            up_to_chapter: 截止到第几章

        Returns:
            角色摘要文本
        """
        history = [
            state for state in self.character_history.get(character_name, [])
            if state.chapter_num <= up_to_chapter
        ]

        if not history:
            return ""

        latest = history[-1]

        summary_parts = [
            f"【{character_name}】",
            f"性格: {latest.personality}",
        ]

        if latest.mood:
            summary_parts.append(f"当前情绪: {latest.mood}")

        if latest.location:
            summary_parts.append(f"当前位置: {latest.location}")

        if latest.relationships:
            rel_text = "; ".join([f"{k}: {v}" for k, v in latest.relationships.items()])
            summary_parts.append(f"人际关系: {rel_text}")

        if latest.goals:
            goals_text = "; ".join(latest.goals)
            summary_parts.append(f"当前目标: {goals_text}")

        if latest.backstory:
            summary_parts.append(f"背景: {latest.backstory}")

        # 新增：下一章注意事项
        if latest.next_chapter_note:
            summary_parts.append(f"下一章注意: {latest.next_chapter_note}")

        return "\n".join(summary_parts)

    def set_next_chapter_note(self, character_name: str, note: str) -> None:
        """
        为角色设置下一章注意事项

        Args:
            character_name: 角色名
            note: 注意事项（如"受伤需要治疗"、"正在寻找某人"等）
        """
        if character_name not in self.character_history:
            logger.warning(f"角色 {character_name} 尚未初始化")
            return

        # 更新最新状态的 note
        latest_state = self.character_history[character_name][-1]
        latest_state.next_chapter_note = note
        logger.info(f"为角色 {character_name} 设置下一章注意: {note}")

    def get_all_next_chapter_notes(self, chapter_num: int) -> str:
        """
        获取所有角色的下一章注意事项，用于生成下一章时的提示

        Args:
            chapter_num: 下一章的章节号

        Returns:
            格式化的注意事项文本
        """
        notes = []

        for char_name, history in self.character_history.items():
            if history:
                latest = history[-1]
                # 只获取当前章节之前的状态的 note
                if latest.next_chapter_note and latest.chapter_num < chapter_num:
                    notes.append(f"- {char_name}: {latest.next_chapter_note}")

        if notes:
            return "【角色延续注意】\n" + "\n".join(notes)
        return ""

    def clear_next_chapter_notes(self, up_to_chapter: int) -> None:
        """
        清除已处理的注意事项

        Args:
            up_to_chapter: 清除到指定章节
        """
        for history in self.character_history.values():
            for state in history:
                if state.chapter_num <= up_to_chapter:
                    state.next_chapter_note = ""

    def save_to_disk(self) -> None:
        """保存数据到磁盘"""
        data = {
            "project_id": self.project_id,
            "character_history": {
                name: [state.to_dict() for state in states]
                for name, states in self.character_history.items()
            },
            "character_events": {
                name: [event.__dict__ for event in events]
                for name, events in self.character_events.items()
            },
            "all_characters": list(self.all_characters),
            "archived_profiles": self.archived_profiles,
            "_update_count": self._update_count
        }

        cache_file = self.cache_dir / f"{self.project_id}_characters.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"角色跟踪数据已保存: {cache_file}")

    def _load_from_disk(self) -> None:
        """从磁盘加载数据"""
        cache_file = self.cache_dir / f"{self.project_id}_characters.json"

        if not cache_file.exists():
            return

        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.all_characters = set(data.get("all_characters", []))

        # 加载角色历史
        for name, states_data in data.get("character_history", {}).items():
            self.character_history[name] = [
                CharacterState.from_dict(state_data)
                for state_data in states_data
            ]

        # 加载角色事件
        for name, events_data in data.get("character_events", {}).items():
            self.character_events[name] = [
                CharacterEvent(**event_data)
                for event_data in events_data
            ]

        # 加载归档档案
        self.archived_profiles = data.get("archived_profiles", {})

        # 加载更新计数
        self._update_count = data.get("_update_count", 0)

        logger.info(f"角色跟踪数据已加载: {cache_file}")


# AI辅助的字符分析功能
def analyze_characters_from_chapter(
    chapter_content: str,
    chapter_num: int,
    tracker: CharacterTracker,
    api_client
) -> List[str]:
    """
    使用AI分析章节内容，提取角色信息

    Args:
        chapter_content: 章节内容
        chapter_num: 章节号
        tracker: 角色跟踪器
        api_client: API客户端（用于AI分析）

    Returns:
        本章节出现的角色名列表
    """
    prompt = f"""分析以下小说章节，提取其中出现的主要角色信息。

章节内容：
{chapter_content[:2000]}

请以JSON格式返回，包含以下字段：
{{
    "characters": [
        {{
            "name": "角色名",
            "personality": "性格特征（简短描述）",
            "mood": "当前情绪",
            "location": "当前位置",
            "goals": ["目标1", "目标2"],
            "backstory": "背景故事（如有提及）"
        }}
    ],
    "relationships": [
        {{
            "character1": "角色1",
            "character2": "角色2",
            "relationship": "关系描述"
        }}
    ]
}}

只返回JSON，不要其他文字。"""

    try:
        response = api_client.generate([
            {"role": "system", "content": "你是一个专业的小说分析助手，擅长提取角色信息。"},
            {"role": "user", "content": prompt}
        ], temperature=0.3)

        import json
        import re

        # 清理响应：移除可能的 Markdown 代码块标记
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        # 尝试解析 JSON，带有容错处理
        if not cleaned_response:
            logger.warning(f"AI角色分析返回空响应")
            return []

        result = _parse_json_with_fallback(cleaned_response, logger, "AI角色分析")

        # 更新角色信息
        characters_found = []
        for char_data in result.get("characters", []):
            name = char_data["name"]
            characters_found.append(name)

            # 记录角色出现
            tracker.track_character_appearance(
                chapter_num,
                name,
                char_data.get("backstory", ""),
                char_data.get("personality")
            )

            # 更新状态
            updates = {}
            if "mood" in char_data:
                updates["mood"] = char_data["mood"]
            if "location" in char_data:
                updates["location"] = char_data["location"]
            if "goals" in char_data:
                updates["goals"] = char_data["goals"]
            if "backstory" in char_data:
                updates["backstory"] = char_data["backstory"]

            if updates:
                tracker.update_character_state(chapter_num, name, updates)

        # 更新关系
        for rel in result.get("relationships", []):
            tracker.track_relationship_change(
                chapter_num,
                rel["character1"],
                rel["character2"],
                rel["relationship"]
            )

        logger.info(f"AI分析完成，发现 {len(characters_found)} 个角色")
        return characters_found

    except Exception as e:
        logger.error(f"AI角色分析失败: {e}")
        return []


def _parse_json_with_fallback(text: str, logger, context: str = "JSON解析"):
    """
    容错的JSON解析函数，尝试修复常见格式问题

    Args:
        text: 要解析的文本
        logger: 日志记录器
        context: 上下文描述

    Returns:
        解析后的字典，失败返回None
    """
    import json
    import re

    def try_parse(data: str) -> dict:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    # 第一次尝试：直接解析
    result = try_parse(text)
    if result:
        return result

    # 第二次尝试：替换中文标点符号
    fixed = text
    chinese_punct_map = {
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '：': ':',
        '，': ',',
        '【': '[',
        '】': ']',
        '（': '(',
        '）': ')',
    }
    for cn, en in chinese_punct_map.items():
        fixed = fixed.replace(cn, en)
    result = try_parse(fixed)
    if result:
        logger.warning(f"{context}: 通过替换中文标点修复成功")
        return result

    # 第三次尝试：修复缺少逗号的问题
    fixed = text
    # 在 } 后面加逗号，如果后面是 " 而不是逗号
    fixed = re.sub(r'}\s*"', '}, "', fixed)
    # 在 ] 后面加逗号
    fixed = re.sub(r']\s*"', '], "', fixed)
    result = try_parse(fixed)
    if result:
        logger.warning(f"{context}: 通过修复逗号成功")
        return result

    # 第四次尝试：提取JSON代码块
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        result = try_parse(json_match.group(0))
        if result:
            logger.warning(f"{context}: 通过提取JSON块成功")
            return result

    # 第五次尝试：使用更宽松的解析
    try:
        # 移除所有换行和多余空格后尝试
        compact = re.sub(r'\s+', ' ', text.strip())
        result = try_parse(compact)
        if result:
            logger.warning(f"{context}: 通过压缩空白成功")
            return result
    except:
        pass

    # 记录原始内容用于调试
    logger.error(f"{context}最终失败，原始内容前500字符: {text[:500]}")
    return None
