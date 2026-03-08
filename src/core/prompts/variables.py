"""
提示词变量系统 - 支持变量替换和动态内容生成

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import re
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptVariableManager:
    """
    提示词变量管理器

    支持的变量：
    - 基础变量：{title}, {genre}, {chapter_num}, etc.
    - 动态变量：{date}, {time}, {timestamp}
    - 条件变量：{if:condition:value}
    - 格式化变量：{uppercase:...}, {lowercase:...}
    """

    # 内置变量定义
    BUILTIN_VARIABLES = {
        # 小说基础信息
        "title": {
            "description": "小说标题",
            "example": "我的玄幻小说"
        },
        "genre": {
            "description": "小说类型",
            "example": "玄幻仙侠"
        },
        "character_setting": {
            "description": "人物设定",
            "example": "主角：张三，性格勇敢..."
        },
        "world_setting": {
            "description": "世界观设定",
            "example": "修仙世界，灵气..."
        },
        "plot_idea": {
            "description": "主线剧情",
            "example": "少年修仙，逆天改命"
        },
        "target_words": {
            "description": "目标字数",
            "example": "3000"
        },
        "chapter_count": {
            "description": "总章节数",
            "example": "100"
        },

        # 章节信息
        "chapter_num": {
            "description": "当前章节号",
            "example": "5"
        },
        "chapter_title": {
            "description": "章节标题",
            "example": "初入仙门"
        },
        "chapter_desc": {
            "description": "章节描述/大纲",
            "example": "主角初次进入修仙门派..."
        },
        "chapter_outline": {
            "description": "章节详细大纲",
            "example": "1. 主角到达门派..."
        },

        # 上下文信息
        "context": {
            "description": "前文回顾/上下文",
            "example": "前几章的主要情节..."
        },
        "previous_chapter": {
            "description": "上一章内容",
            "example": "上一章的完整内容..."
        },
        "character_states": {
            "description": "角色当前状态",
            "example": "张三：练气期三层..."
        },
        "plot_progress": {
            "description": "剧情进展",
            "example": "主线：刚刚进入门派..."
        },

        # 生成参数
        "style": {
            "description": "写作风格",
            "example": "古典仙侠"
        },
        "temperature": {
            "description": "生成温度（0-1）",
            "example": "0.8"
        },
        "max_tokens": {
            "description": "最大token数",
            "example": "4000"
        },

        # 重写相关
        "content": {
            "description": "待重写的内容",
            "example": "原始内容..."
        },
        "rewrite_style": {
            "description": "重写风格",
            "example": "更生动细腻"
        },

        # 时间变量
        "date": {
            "description": "当前日期",
            "example": "2026-02-07"
        },
        "time": {
            "description": "当前时间",
            "example": "22:30:45"
        },
        "timestamp": {
            "description": "时间戳",
            "example": "2026-02-07 22:30:45"
        },
    }

    def __init__(self):
        """初始化变量管理器"""
        # 自定义变量处理器
        self.custom_handlers: Dict[str, callable] = {}

    def apply_variables(
        self,
        template: str,
        variables: Dict[str, Any],
        recursive: bool = True
    ) -> str:
        """
        应用变量替换

        Args:
            template: 模板字符串
            variables: 变量字典
            recursive: 是否递归替换（支持变量嵌套）

        Returns:
            替换后的字符串
        """
        result = template
        max_iterations = 10  # 防止无限循环

        for _ in range(max_iterations if recursive else 1):
            old_result = result

            # 替换内置变量
            for key, value in variables.items():
                if value is None:
                    value = ""

                # 将值转换为字符串
                value_str = str(value)

                # 替换 {key} 格式
                result = result.replace(f"{{{key}}}", value_str)

            # 处理动态变量（日期时间）
            result = self._process_dynamic_variables(result)

            # 处理条件变量
            result = self._process_conditional_variables(result, variables)

            # 处理格式化变量
            result = self._process_format_variables(result)

            # 处理自定义变量
            for pattern, handler in self.custom_handlers.items():
                result = re.sub(pattern, handler, result)

            # 如果没有变化，提前退出
            if result == old_result:
                break

        return result

    def _process_dynamic_variables(self, text: str) -> str:
        """处理动态变量（日期时间等）"""
        now = datetime.now()

        # 替换日期时间变量
        text = text.replace("{date}", now.strftime("%Y-%m-%d"))
        text = text.replace("{time}", now.strftime("%H:%M:%S"))
        text = text.replace("{timestamp}", now.strftime("%Y-%m-%d %H:%M:%S"))

        return text

    def _process_conditional_variables(
        self,
        text: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        处理条件变量

        格式：{if:variable:value_if_true} 或 {if:variable:value_if_true:value_if_false}
        """
        pattern = r'\{if:(\w+):([^}:]*)(?::([^}]*))?\}'

        def replace_conditional(match):
            var_name = match.group(1)
            true_value = match.group(2)
            false_value = match.group(3) if match.group(3) else ""

            # 检查变量是否存在且为真值
            var_value = variables.get(var_name)
            if var_value:
                # 检查是否为特定的真值
                if isinstance(var_value, str):
                    return true_value if var_value.lower() not in ('false', '', '0', 'no') else false_value
                return true_value if var_value else false_value

            return false_value

        return re.sub(pattern, replace_conditional, text)

    def _process_format_variables(self, text: str) -> str:
        """
        处理格式化变量

        格式：
        - {uppercase:value} - 转大写
        - {lowercase:value} - 转小写
        - {capitalize:value} - 首字母大写
        - {length:value} - 字符串长度
        """
        # 转大写
        text = re.sub(r'\{uppercase:([^}]+)\}', lambda m: m.group(1).upper(), text)

        # 转小写
        text = re.sub(r'\{lowercase:([^}]+)\}', lambda m: m.group(1).lower(), text)

        # 首字母大写
        text = re.sub(r'\{capitalize:([^}]+)\}', lambda m: m.group(1).capitalize(), text)

        return text

    def register_custom_handler(
        self,
        pattern: str,
        handler: callable
    ) -> None:
        """
        注册自定义变量处理器

        Args:
            pattern: 正则表达式模式
            handler: 处理函数，接收match对象，返回替换字符串
        """
        self.custom_handlers[pattern] = handler
        logger.info(f"注册自定义变量处理器: {pattern}")

    def get_variables_info(self) -> List[Dict[str, str]]:
        """
        获取所有可用变量的信息

        Returns:
            变量信息列表
        """
        variables = []

        for name, info in self.BUILTIN_VARIABLES.items():
            variables.append({
                "name": name,
                "description": info["description"],
                "example": info["example"]
            })

        # 按名称排序
        variables.sort(key=lambda x: x["name"])

        return variables

    def validate_template(self, template: str) -> List[str]:
        """
        验证模板中的变量

        Args:
            template: 模板字符串

        Returns:
            未定义的变量列表（警告）
        """
        # 提取所有变量
        pattern = r'\{([^}:]+)(?::[^}]*)?\}'
        matches = re.findall(pattern, template)

        undefined = []
        for match in matches:
            # 跳过条件变量和格式化变量
            if match in ('if', 'uppercase', 'lowercase', 'capitalize'):
                continue

            # 检查是否为内置变量
            if match not in self.BUILTIN_VARIABLES:
                undefined.append(match)

        return list(set(undefined))

    def extract_variables(self, template: str) -> List[str]:
        """
        提取模板中使用的所有变量

        Args:
            template: 模板字符串

        Returns:
            变量名列表
        """
        # 提取简单的 {variable} 格式
        pattern = r'\{(\w+)\}'
        matches = re.findall(pattern, template)

        # 去重并排序
        return sorted(set(matches))


# 便捷函数
def create_generation_prompt(
    template: str,
    title: str,
    genre: str,
    chapter_num: int,
    chapter_title: str,
    chapter_desc: str,
    context: str = "",
    target_words: int = 3000,
    style: str = "",
    **kwargs
) -> str:
    """
    创建生成章节的提示词

    Args:
        template: 提示词模板
        title: 标题
        genre: 类型
        chapter_num: 章节号
        chapter_title: 章节标题
        chapter_desc: 章节描述
        context: 上下文
        target_words: 目标字数
        style: 风格
        **kwargs: 其他变量

    Returns:
        完整的提示词
    """
    manager = PromptVariableManager()

    variables = {
        "title": title,
        "genre": genre,
        "chapter_num": chapter_num,
        "chapter_title": chapter_title,
        "chapter_desc": chapter_desc,
        "context": context,
        "target_words": target_words,
        "style": style,
        **kwargs
    }

    return manager.apply_variables(template, variables)


def create_rewrite_prompt(
    template: str,
    content: str,
    rewrite_style: str = "",
    **kwargs
) -> str:
    """
    创建重写的提示词

    Args:
        template: 提示词模板
        content: 待重写内容
        rewrite_style: 重写风格
        **kwargs: 其他变量

    Returns:
        完整的提示词
    """
    manager = PromptVariableManager()

    variables = {
        "content": content,
        "rewrite_style": rewrite_style,
        **kwargs
    }

    return manager.apply_variables(template, variables)
