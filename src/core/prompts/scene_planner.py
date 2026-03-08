"""
场景拆分策略 - 解决字数控制难题
通过场景规划实现精确字数控制

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
"""

import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class ScenePlanner:
    """
    场景规划器 - 将章节拆分为多个场景，精确控制字数

    核心思想：
    - 3000字章节 = 3-5个场景
    - 每个场景有明确字数分配
    - 场景之间有过渡衔接
    """

    # 场景类型模板
    SCENE_TYPES = {
        "opening": {
            "name": "开场场景",
            "description": "引入本章，承接上文，设定基调",
            "ratio": 0.15,  # 占章节15%
            "elements": ["环境描写", "人物状态", "承接上文"]
        },
        "development": {
            "name": "发展场景",
            "description": "推进剧情，展开冲突",
            "ratio": 0.30,  # 占章节30%
            "elements": ["对话互动", "行动推进", "信息揭示"]
        },
        "climax": {
            "name": "高潮场景",
            "description": "本章重点，情感或行动高潮",
            "ratio": 0.35,  # 占章节35%
            "elements": ["冲突爆发", "情感爆发", "关键行动"]
        },
        "ending": {
            "name": "收尾场景",
            "description": "收束本章，铺垫下章",
            "ratio": 0.20,  # 占章节20%
            "elements": ["结果展示", "伏笔埋设", "过渡到下章"]
        }
    }

    @classmethod
    def plan_scenes(cls, target_words: int, chapter_desc: str, context_hint: str = "") -> List[Dict]:
        """
        规划章节场景

        Args:
            target_words: 目标字数
            chapter_desc: 章节描述
            context_hint: 上下文提示

        Returns:
            场景列表，每个场景包含字数分配
        """
        # 确定场景数量（根据字数调整）
        if target_words <= 1500:
            scene_count = 2
        elif target_words <= 3000:
            scene_count = 3
        elif target_words <= 5000:
            scene_count = 4
        else:
            scene_count = 5

        # 计算每个场景的字数分配
        base_words = target_words // scene_count
        remainder = target_words % scene_count

        scenes = []
        scene_names = ["开场", "发展", "高潮", "收尾", "过渡"]

        for i in range(scene_count):
            # 最后一个场景加上余数
            scene_words = base_words + (remainder if i == scene_count - 1 else 0)

            scene = {
                "order": i + 1,
                "name": scene_names[i] if i < len(scene_names) else f"场景{i+1}",
                "target_words": scene_words,
                "purpose": cls._get_scene_purpose(i, scene_count, chapter_desc),
                "key_elements": cls._get_scene_elements(i, scene_count),
                "connection_from": f"场景{i}" if i > 0 else None,
                "connection_to": f"场景{i+2}" if i < scene_count - 1 else None
            }
            scenes.append(scene)

        logger.info(f"规划了 {scene_count} 个场景，总字数: {target_words}")
        return scenes

    @classmethod
    def _get_scene_purpose(cls, scene_index: int, total_scenes: int, chapter_desc: str) -> str:
        """获取场景目的"""
        purposes = [
            "承接上文，引入本章情节",
            "展开剧情，推进冲突发展",
            "达到本章高潮，情感或行动爆发",
            "收束本章，埋设下章伏笔"
        ]
        if scene_index < len(purposes):
            return purposes[scene_index]
        return "推进剧情"

    @classmethod
    def _get_scene_elements(cls, scene_index: int, total_scenes: int) -> List[str]:
        """获取场景关键要素"""
        if scene_index == 0:
            return ["环境描写", "人物出场", "状态交代"]
        elif scene_index == total_scenes - 1:
            return ["结果展示", "伏笔埋设", "过渡衔接"]
        else:
            return ["对话互动", "行动推进", "信息揭示"]


def build_scene_based_prompt(
    chapter_title: str,
    chapter_desc: str,
    scenes: List[Dict],
    context_text: str,
    coherence_info: str
) -> str:
    """
    构建基于场景拆分的生成提示词

    Args:
        chapter_title: 章节标题
        chapter_desc: 章节描述
        scenes: 场景规划
        context_text: 上下文文本
        coherence_info: 连贯性信息

    Returns:
        完整提示词
    """
    # 构建场景说明
    scene_parts = []
    total_words = sum(s["target_words"] for s in scenes)

    scene_parts.append(f"【章节结构规划】")
    scene_parts.append(f"本章共分{len(scenes)}个场景，总字数约{total_words}字：\n")

    for scene in scenes:
        scene_parts.append(
            f"场景{scene['order']}：{scene['name']}（约{scene['target_words']}字）\n"
            f"- 目的：{scene['purpose']}\n"
            f"- 要素：{', '.join(scene['key_elements'])}"
        )
        if scene.get("connection_from"):
            scene_parts.append(f"- 衔接：承接{scene['connection_from']}")
        if scene.get("connection_to"):
            scene_parts.append(f"- 衔接：过渡到{scene['connection_to']}")

    prompt = f"""{context_text}

{coherence_info}

【当前章节】
第{chapter_title.split()[0] if '章' in chapter_title else ''}章：{chapter_title}

【章节要求】
{chapter_desc}

{chr(10).join(scene_parts)}

【创作要求】
1. 严格按照场景规划执行，每个场景控制在指定字数范围±10%
2. 场景之间要有自然的过渡衔接
3. 每个场景完成其指定目的
4. 整体字数控制在约{total_words}字

请开始创作，请按场景顺序逐步展开：
"""

    return prompt


# 场景规划提示词模板
SCENE_PLANNING_PROMPT = """请根据以下章节描述，规划详细的场景结构。

【章节信息】
章节标题：{chapter_title}
章节描述：{chapter_desc}
目标字数：{target_words}字

【场景规划要求】
1. 将章节拆分为3-5个场景
2. 每个场景包含：场景名称、目的、字数分配、关键要素
3. 场景之间要有逻辑衔接
4. 场景类型包括：开场、发展、高潮、收尾

【输出格式】
场景1：[名称]（约XXX字）
- 目的：...
- 关键要素：...
- 衔接：...

场景2：[名称]（约XXX字）
- 目的：...
- 关键要素：...
- 衔接：...

请开始规划："""


def parse_scene_plan(plan_text: str) -> List[Dict]:
    """
    解析AI返回的场景规划

    Args:
        plan_text: 场景规划文本

    Returns:
        场景列表
    """
    import re

    scenes = []
    # 匹配场景定义
    pattern = r'场景(\d+)[:：]\s*([^\n（\(]+)[（\(]约(\d+)字[）\)]'

    matches = re.findall(pattern, plan_text)
    for match in matches:
        scene_num = int(match[0])
        scene_name = match[1].strip()
        scene_words = int(match[1])
        scenes.append({
            "order": scene_num,
            "name": scene_name,
            "target_words": scene_words,
            "purpose": "",
            "key_elements": []
        })

    if not scenes:
        # 解析失败，使用默认规划
        logger.warning("解析场景规划失败，使用默认规划")
        return []

    logger.info(f"成功解析 {len(scenes)} 个场景")
    return scenes
