"""
世界观数据库 - 维护世界设定的完整性和一致性

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
class Location:
    """地点"""
    name: str                      # 名称
    type: str                      # 类型（city/forest/building/etc）
    description: str               # 描述
    features: List[str] = field(default_factory=list)  # 特征
    related_locations: List[str] = field(default_factory=list)  # 相关地点
    first_appeared_chapter: int = 0  # 首次出现章节


@dataclass
class Item:
    """重要物品"""
    name: str                      # 名称
    type: str                      # 类型（weapon/artifact/magic_item/etc）
    description: str               # 描述
    powers: List[str] = field(default_factory=list)  # 能力/功能
    owner: Optional[str] = None    # 当前持有者
    location: Optional[str] = None  # 当前位置
    first_appeared_chapter: int = 0  # 首次出现章节


@dataclass
class WorldRule:
    """世界规则（如魔法系统、科技水平等）"""
    name: str                      # 规则名称
    category: str                  # 类别（magic/technology/physics/society/etc）
    description: str               # 规则描述
    constraints: List[str] = field(default_factory=list)  # 限制条件
    examples: List[str] = field(default_factory=list)  # 示例


@dataclass
class TimelineEvent:
    """时间线事件"""
    chapter_num: int               # 章节
    event_type: str                # 事件类型（plot/character/world_change）
    description: str               # 事件描述
    related_characters: List[str] = field(default_factory=list)  # 相关角色
    related_locations: List[str] = field(default_factory=list)  # 相关地点


class WorldDatabase:
    """
    世界观数据库

    功能：
    1. 维护地点、物品、规则等世界设定
    2. 检查设定的一致性
    3. 提供世界观查询
    4. 生成世界观上下文
    """

    def __init__(self, project_id: str, cache_dir: Optional[Path] = None):
        """
        初始化世界观数据库

        Args:
            project_id: 项目ID
            cache_dir: 缓存目录
        """
        self.project_id = project_id
        self.cache_dir = cache_dir or get_cache_dir() / "coherence"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 地点
        self.locations: Dict[str, Location] = {}

        # 物品
        self.items: Dict[str, Item] = {}

        # 世界规则
        self.rules: Dict[str, WorldRule] = {}

        # 时间线
        self.timeline: List[TimelineEvent] = []

        # 加载已有数据
        self._load_from_disk()

    def add_location(
        self,
        name: str,
        location_type: str,
        description: str,
        features: Optional[List[str]] = None,
        chapter_num: int = 0
    ) -> Location:
        """
        添加地点

        Args:
            name: 名称
            location_type: 类型
            description: 描述
            features: 特征
            chapter_num: 章节号

        Returns:
            Location对象
        """
        location = Location(
            name=name,
            type=location_type,
            description=description,
            features=features or [],
            first_appeared_chapter=chapter_num
        )

        self.locations[name] = location
        logger.info(f"添加地点: {name} ({location_type})")
        return location

    def update_location(self, name: str, **updates) -> None:
        """
        更新地点信息

        Args:
            name: 地点名称
            **updates: 更新的字段
        """
        if name not in self.locations:
            logger.warning(f"地点 {name} 不存在")
            return

        location = self.locations[name]
        for key, value in updates.items():
            if hasattr(location, key):
                setattr(location, key, value)

        logger.info(f"更新地点: {name}")

    def add_item(
        self,
        name: str,
        item_type: str,
        description: str,
        powers: Optional[List[str]] = None,
        owner: Optional[str] = None,
        chapter_num: int = 0
    ) -> Item:
        """
        添加物品

        Args:
            name: 名称
            item_type: 类型
            description: 描述
            powers: 能力
            owner: 持有者
            chapter_num: 章节号

        Returns:
            Item对象
        """
        item = Item(
            name=name,
            type=item_type,
            description=description,
            powers=powers or [],
            owner=owner,
            first_appeared_chapter=chapter_num
        )

        self.items[name] = item
        logger.info(f"添加物品: {name} ({item_type})")
        return item

    def update_item(self, name: str, **updates) -> None:
        """
        更新物品信息

        Args:
            name: 物品名称
            **updates: 更新的字段
        """
        if name not in self.items:
            logger.warning(f"物品 {name} 不存在")
            return

        item = self.items[name]
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)

        logger.info(f"更新物品: {name}")

    def add_rule(
        self,
        name: str,
        category: str,
        description: str,
        constraints: Optional[List[str]] = None,
        examples: Optional[List[str]] = None
    ) -> WorldRule:
        """
        添加世界规则

        Args:
            name: 规则名称
            category: 类别
            description: 描述
            constraints: 限制条件
            examples: 示例

        Returns:
            WorldRule对象
        """
        rule = WorldRule(
            name=name,
            category=category,
            description=description,
            constraints=constraints or [],
            examples=examples or []
        )

        self.rules[name] = rule
        logger.info(f"添加世界规则: {name} ({category})")
        return rule

    def add_timeline_event(
        self,
        chapter_num: int,
        event_type: str,
        description: str,
        related_characters: Optional[List[str]] = None,
        related_locations: Optional[List[str]] = None
    ) -> TimelineEvent:
        """
        添加时间线事件

        Args:
            chapter_num: 章节号
            event_type: 事件类型
            description: 描述
            related_characters: 相关角色
            related_locations: 相关地点

        Returns:
            TimelineEvent对象
        """
        event = TimelineEvent(
            chapter_num=chapter_num,
            event_type=event_type,
            description=description,
            related_characters=related_characters or [],
            related_locations=related_locations or []
        )

        self.timeline.append(event)
        # 按章节排序
        self.timeline.sort(key=lambda e: e.chapter_num)

        logger.info(f"添加时间线事件: 第{chapter_num}章 - {description[:50]}")
        return event

    def check_consistency(self, new_content: str) -> List[str]:
        """
        检查新内容与世界设定的一致性

        Args:
            new_content: 新生成的内容

        Returns:
            问题列表
        """
        issues = []

        # 简化的检查：查找可能违反设定的关键词
        # 实际应该使用AI进行语义分析

        content_lower = new_content.lower()

        # 检查地点描述的一致性
        for loc_name, loc in self.locations.items():
            if loc_name in new_content:
                # 检查是否有与已知特征矛盾的地方
                for feature in loc.features:
                    # 这里简化处理，实际应该用AI理解语义
                    pass

        # 检查物品使用是否符合规则
        for item_name, item in self.items.items():
            if item_name in new_content:
                # 检查物品的使用方式是否符合其能力描述
                pass

        # 检查是否违反世界规则
        for rule_name, rule in self.rules.items():
            # 简化：检查规则关键词
            if rule.category == "magic" and "魔法" in new_content:
                # 应该检查魔法使用是否符合规则
                pass

        return issues

    def get_relevant_context(self, topic: str, max_length: int = 300) -> str:
        """
        根据主题获取相关的世界观信息

        Args:
            topic: 主题（如地点名、物品名等）
            max_length: 最大长度

        Returns:
            相关的世界观描述
        """
        context_parts = []

        # 查找相关地点
        for loc_name, loc in self.locations.items():
            if loc_name in topic:
                parts = [f"【{loc_name}】", f"类型: {loc.type}", loc.description]
                if loc.features:
                    parts.append(f"特征: {', '.join(loc.features)}")
                context_parts.append("\n".join(parts))

        # 查找相关物品
        for item_name, item in self.items.items():
            if item_name in topic:
                parts = [f"【{item_name}】", f"类型: {item.type}", item.description]
                if item.powers:
                    parts.append(f"能力: {', '.join(item.powers)}")
                if item.owner:
                    parts.append(f"持有者: {item.owner}")
                context_parts.append("\n".join(parts))

        # 查找相关规则
        for rule_name, rule in self.rules.items():
            if rule_name in topic or rule.category in topic:
                parts = [f"【{rule_name}】", f"类别: {rule.category}", rule.description]
                if rule.constraints:
                    parts.append(f"限制: {', '.join(rule.constraints)}")
                context_parts.append("\n".join(parts))

        context = "\n\n".join(context_parts)

        # 截断到最大长度
        if len(context) > max_length:
            context = context[:max_length] + "..."

        return context

    def get_world_summary(self, max_items: int = 5) -> str:
        """
        生成世界观数据库摘要

        Args:
            max_items: 每类最多返回几项

        Returns:
            摘要文本
        """
        summary_parts = ["【世界观设定】"]

        # 地点
        if self.locations:
            locations = list(self.locations.values())[:max_items]
            loc_text = "\n".join([
                f"  - {loc.name}（{loc.type}）: {loc.description[:50]}..."
                for loc in locations
            ])
            summary_parts.append(f"\n地点:\n{loc_text}")

        # 重要物品
        if self.items:
            items = list(self.items.values())[:max_items]
            item_text = "\n".join([
                f"  - {item.name}（{item.type}）: {item.description[:50]}..."
                for item in items
            ])
            summary_parts.append(f"\n重要物品:\n{item_text}")

        # 世界规则
        if self.rules:
            rules = list(self.rules.values())[:max_items]
            rule_text = "\n".join([
                f"  - {rule.name}（{rule.category}）: {rule.description[:50]}..."
                for rule in rules
            ])
            summary_parts.append(f"\n世界规则:\n{rule_text}")

        return "\n".join(summary_parts)

    def save_to_disk(self) -> None:
        """保存数据到磁盘"""
        data = {
            "project_id": self.project_id,
            "locations": {
                name: asdict(loc)
                for name, loc in self.locations.items()
            },
            "items": {
                name: asdict(item)
                for name, item in self.items.items()
            },
            "rules": {
                name: asdict(rule)
                for name, rule in self.rules.items()
            },
            "timeline": [event.__dict__ for event in self.timeline]
        }

        cache_file = self.cache_dir / f"{self.project_id}_world.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"世界观数据已保存: {cache_file}")

    def _load_from_disk(self) -> None:
        """从磁盘加载数据"""
        cache_file = self.cache_dir / f"{self.project_id}_world.json"

        if not cache_file.exists():
            return

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 加载地点
            for name, loc_data in data.get("locations", {}).items():
                self.locations[name] = Location(**loc_data)

            # 加载物品
            for name, item_data in data.get("items", {}).items():
                self.items[name] = Item(**item_data)

            # 加载规则
            for name, rule_data in data.get("rules", {}).items():
                self.rules[name] = WorldRule(**rule_data)

            # 加载时间线
            for event_data in data.get("timeline", []):
                self.timeline.append(TimelineEvent(**event_data))

            logger.info(f"世界观数据已加载: {cache_file}")

        except Exception as e:
            logger.error(f"加载世界观数据失败: {e}")


# AI辅助的世界观提取功能
def extract_world_setting_from_chapter(
    chapter_content: str,
    chapter_num: int,
    world_db: WorldDatabase,
    api_client
) -> None:
    """
    使用AI从章节中提取世界观信息

    Args:
        chapter_content: 章节内容
        chapter_num: 章节号
        world_db: 世界观数据库
        api_client: API客户端
    """
    logger.info(f"[世界观提取] 开始从第{chapter_num}章提取世界观设定")

    prompt = f"""分析以下小说章节，提取世界观设定信息。

章节内容：
{chapter_content[:2000]}

请以JSON格式返回，包含以下字段：
{{
    "locations": [
        {{
            "name": "地点名称",
            "type": "类型（city/forest/building/etc）",
            "description": "描述",
            "features": ["特征1", "特征2"]
        }}
    ],
    "items": [
        {{
            "name": "物品名称",
            "type": "类型（weapon/artifact/magic_item/etc）",
            "description": "描述",
            "powers": ["能力1", "能力2"],
            "owner": "持有者（如有）"
        }}
    ],
    "rules": [
        {{
            "name": "规则名称",
            "category": "类别（magic/technology/physics/society/etc）",
            "description": "规则描述",
            "constraints": ["限制1", "限制2"]
        }}
    ]
}}

只返回JSON，不要其他文字。如果某类信息没有，返回空列表。"""

    try:
        response = api_client.generate([
            {"role": "system", "content": "你是一个专业的小说分析助手，擅长提取世界观设定。"},
            {"role": "user", "content": prompt}
        ], temperature=0.3)

        # 检查响应是否为空或无效
        if not response or not response.strip():
            logger.warning("AI返回空响应，使用空世界观配置")
            return

        # 清理响应内容（去除markdown代码块）
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        # 尝试解析JSON
        try:
            result = json.loads(cleaned_response)
        except json.JSONDecodeError as je:
            logger.warning(f"AI返回的不是有效JSON: {je}，原始响应: {response[:100]}...")
            return

        # 检查是否为字典类型
        if not isinstance(result, dict):
            logger.warning(f"AI返回的不是字典类型: {type(result)}")
            return

        # 添加地点
        for loc_data in result.get("locations", []):
            world_db.add_location(
                name=loc_data["name"],
                location_type=loc_data["type"],
                description=loc_data["description"],
                features=loc_data.get("features", []),
                chapter_num=chapter_num
            )

        # 添加物品
        for item_data in result.get("items", []):
            world_db.add_item(
                name=item_data["name"],
                item_type=item_data["type"],
                description=item_data["description"],
                powers=item_data.get("powers", []),
                owner=item_data.get("owner"),
                chapter_num=chapter_num
            )

        # 添加规则
        for rule_data in result.get("rules", []):
            world_db.add_rule(
                name=rule_data["name"],
                category=rule_data["category"],
                description=rule_data["description"],
                constraints=rule_data.get("constraints", []),
                examples=rule_data.get("examples", [])
            )

        logger.info(f"[世界观提取] AI世界观提取完成，提取了{len(result.get('locations', []))}个地点，{len(result.get('items', []))}个物品，{len(result.get('rules', []))}个规则")

    except Exception as e:
        logger.error(f"[世界观提取] AI世界观提取失败: {e}", exc_info=True)
