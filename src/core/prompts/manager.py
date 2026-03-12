"""
提示词管理器 - 管理提示词模板、变量替换、导入导出

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from ...config.paths import get_config_dir
from datetime import datetime

from .templates import PRESET_TEMPLATES
from .variables import PromptVariableManager

logger = logging.getLogger(__name__)


class PromptManager:
    """
    提示词管理器

    功能：
    1. 管理提示词模板
    2. 变量替换
    3. 导入/导出配置
    4. 预设模板管理
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化提示词管理器

        Args:
            config_dir: 配置目录
        """
        self.config_dir = config_dir or get_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 自定义模板 {category: {name: template}}
        self.custom_templates: Dict[str, Dict[str, str]] = {}

        # 变量管理器
        self.variable_manager = PromptVariableManager()

        # 加载自定义模板
        self._load_custom_templates()

        logger.info(f"[提示词管理] PromptManager初始化完成，配置目录: {self.config_dir}")

    def get_template(
        self,
        category: str,
        name: str,
        use_preset: bool = True
    ) -> Optional[str]:
        """
        获取提示词模板

        Args:
            category: 类别（如 "generation", "rewrite", "outline"）
            name: 模板名称
            use_preset: 是否查找预设模板

        Returns:
            模板内容，如果不存在则返回None
        """
        # 先查找自定义模板
        if category in self.custom_templates and name in self.custom_templates[category]:
            return self.custom_templates[category][name]

        # 查找预设模板
        if use_preset:
            preset_key = f"{category} - {name}" if category != "preset" else name
            if preset_key in PRESET_TEMPLATES:
                return PRESET_TEMPLATES[preset_key]

        return None

    def set_template(
        self,
        category: str,
        name: str,
        template: str
    ) -> None:
        """
        设置自定义模板

        Args:
            category: 类别
            name: 模板名称
            template: 模板内容
        """
        if category not in self.custom_templates:
            self.custom_templates[category] = {}

        self.custom_templates[category][name] = template

        logger.info(f"[提示词管理] 设置自定义模板: {category} - {name} ({len(template)} 字符)")

        # 保存到磁盘
        self._save_custom_templates()

    def delete_template(
        self,
        category: str,
        name: str
    ) -> bool:
        """
        删除自定义模板

        Args:
            category: 类别
            name: 模板名称

        Returns:
            是否成功删除
        """
        if category in self.custom_templates and name in self.custom_templates[category]:
            del self.custom_templates[category][name]
            self._save_custom_templates()
            logger.info(f"[提示词管理] 删除自定义模板: {category} - {name}")
            return True

        logger.warning(f"[提示词管理] 尝试删除不存在的模板: {category} - {name}")
        return False

    def list_templates(
        self,
        category: Optional[str] = None,
        include_preset: bool = True
    ) -> Dict[str, List[str]]:
        """
        列出所有模板

        Args:
            category: 指定类别，None表示所有
            include_preset: 是否包含预设模板

        Returns:
            {category: [template_names]}
        """
        result = {}

        # 自定义模板
        if category:
            if category in self.custom_templates:
                result[category] = list(self.custom_templates[category].keys())
        else:
            for cat, templates in self.custom_templates.items():
                result[cat] = list(templates.keys())

        # 预设模板
        if include_preset:
            preset_categories = {}
            for key in PRESET_TEMPLATES.keys():
                if " - " in key:
                    cat, name = key.split(" - ", 1)
                    if cat not in preset_categories:
                        preset_categories[cat] = []
                    preset_categories[cat].append(name)

            if category:
                if category in preset_categories:
                    if category not in result:
                        result[category] = []
                    result[category].extend(preset_categories[category])
            else:
                for cat, names in preset_categories.items():
                    if cat not in result:
                        result[cat] = []
                    result[cat].extend(names)

        return result

    def apply_variables(
        self,
        template: str,
        variables: Dict[str, str]
    ) -> str:
        """
        应用变量替换

        Args:
            template: 模板内容
            variables: 变量字典

        Returns:
            替换后的内容
        """
        return self.variable_manager.apply_variables(template, variables)

    def get_available_variables(self) -> List[Dict[str, str]]:
        """
        获取可用的变量列表

        Returns:
            变量信息列表 [{name, description, example}]
        """
        return self.variable_manager.get_variables_info()

    def export_templates(
        self,
        categories: Optional[List[str]] = None
    ) -> str:
        """
        导出模板配置为JSON

        Args:
            categories: 要导出的类别，None表示全部

        Returns:
            JSON字符串
        """
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "templates": {}
        }

        for category, templates in self.custom_templates.items():
            if categories and category not in categories:
                continue

            export_data["templates"][category] = templates

        return json.dumps(export_data, ensure_ascii=False, indent=2)

    def import_templates(
        self,
        json_str: str,
        overwrite: bool = False
    ) -> int:
        """
        导入模板配置

        Args:
            json_str: JSON字符串
            overwrite: 是否覆盖已存在的模板

        Returns:
            导入的模板数量
        """
        try:
            data = json.loads(json_str)

            if "templates" not in data:
                logger.warning("导入数据中没有templates字段")
                return 0

            count = 0
            for category, templates in data["templates"].items():
                if category not in self.custom_templates:
                    self.custom_templates[category] = {}

                for name, template in templates.items():
                    # 检查是否已存在
                    if not overwrite and name in self.custom_templates[category]:
                        logger.info(f"跳过已存在的模板: {category} - {name}")
                        continue

                    self.custom_templates[category][name] = template
                    count += 1

            # 保存
            self._save_custom_templates()

            logger.info(f"[提示词管理] 成功导入 {count} 个模板（覆盖: {overwrite}）")
            return count

        except Exception as e:
            logger.error(f"[提示词管理] 导入模板失败: {e}", exc_info=True)
            return 0

    def reset_to_preset(
        self,
        category: str,
        name: str
    ) -> bool:
        """
        重置为预设模板

        Args:
            category: 类别
            name: 模板名称

        Returns:
            是否成功
        """
        preset_key = f"{category} - {name}"
        if preset_key not in PRESET_TEMPLATES:
            return False

        # 删除自定义版本，使用预设版本
        if category in self.custom_templates and name in self.custom_templates[category]:
            del self.custom_templates[category][name]
            self._save_custom_templates()

        return True

    def get_template_for_generation(
        self,
        template_str: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
        category: str = "generation",
        default_template: str = "默认"
    ) -> str:
        """
        获取用于生成的完整提示词

        Args:
            template_str: 自定义模板字符串（如果提供，直接使用）
            variables: 变量字典
            category: 模板类别
            default_template: 默认模板名称

        Returns:
            完整的提示词
        """
        # 如果提供了自定义模板，直接使用
        if template_str:
            template = template_str
        else:
            # 否则获取模板
            template = self.get_template(category, default_template)
            if not template:
                # 如果没有找到，使用简单的默认模板
                template = self._get_fallback_template(category)

        # 应用变量
        if variables:
            template = self.apply_variables(template, variables)

        return template

    def _get_fallback_template(self, category: str) -> str:
        """获取备用模板"""
        if category == "generation":
            return """请根据以下信息生成小说章节：

标题：{title}
类型：{genre}
章节：第{chapter_num}章 - {chapter_title}
章节描述：{chapter_desc}

上下文：
{context}

请生成约 {target_words} 字的内容。"""

        elif category == "rewrite":
            return "请重写以下内容，使用更生动细腻的笔触：\n\n{content}"

        elif category == "outline":
            return """请为以下小说创建大纲：

标题：{title}
类型：{genre}
人物设定：{character_setting}
世界观：{world_setting}
主线剧情：{plot_idea}

请生成 {chapter_count} 章的详细大纲。"""

        return "{content}"

    def _load_custom_templates(self) -> None:
        """从磁盘加载自定义模板"""
        config_file = self.config_dir / "custom_prompts.json"

        if not config_file.exists():
            return

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.custom_templates = data.get("templates", {})
            total_templates = sum(len(templates) for templates in self.custom_templates.values())
            logger.info(f"[提示词管理] 加载自定义模板: {len(self.custom_templates)} 个类别，共 {total_templates} 个模板")

        except Exception as e:
            logger.error(f"[提示词管理] 加载自定义模板失败: {e}", exc_info=True)

    def _save_custom_templates(self) -> None:
        """保存自定义模板到磁盘"""
        config_file = self.config_dir / "custom_prompts.json"

        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "templates": self.custom_templates
        }

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            total_templates = sum(len(templates) for templates in self.custom_templates.values())
            logger.info(f"[提示词管理] 保存自定义模板: {config_file}, 共 {total_templates} 个模板")

        except Exception as e:
            logger.error(f"[提示词管理] 保存自定义模板失败: {e}", exc_info=True)


# 便捷函数
def get_prompt_manager(config_dir: Optional[Path] = None) -> PromptManager:
    """
    获取提示词管理器实例

    Args:
        config_dir: 配置目录

    Returns:
        PromptManager实例
    """
    return PromptManager(config_dir)
