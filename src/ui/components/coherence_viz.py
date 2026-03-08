"""
连贯性可视化UI组件 - 角色状态、剧情线、验证报告可视化

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import gradio as gr
from typing import List, Dict, Optional
import json
from datetime import datetime


class CoherenceVizUI:
    """连贯性可视化UI组件"""

    def __init__(self, app_state):
        """
        初始化连贯性可视化UI

        Args:
            app_state: 应用状态对象
        """
        self.app_state = app_state

    def create_ui(self) -> gr.Blocks:
        """创建连贯性可视化UI"""
        with gr.Blocks() as viz_ui:
            gr.Markdown("## 🔍 连贯性分析")

            # 项目选择器（放在最上面）
            with gr.Row():
                # 获取初始项目列表
                initial_projects = self._load_initial_projects()
                self.project_selector = gr.Dropdown(
                    label="📁 选择项目",
                    choices=initial_projects,
                    value=None,
                    interactive=True,
                    info="先选择项目，然后查看该项目的连贯性分析"
                )
                self.refresh_projects_btn = gr.Button("🔄 刷新项目列表", size="sm")

            # 项目信息显示
            self.project_info = gr.Markdown("**请先选择一个项目**")

            gr.Markdown("---")

            with gr.Tabs():
                # Tab 1: 角色状态
                with gr.Tab("👥 角色状态"):
                    gr.Markdown("### 角色状态跟踪")

                    with gr.Row():
                        self.character_dropdown = gr.Dropdown(
                            label="选择角色",
                            choices=[],
                            value=None,
                            interactive=True
                        )
                        self.refresh_chars_btn = gr.Button("🔄 刷新", size="sm")

                    # 角色基本信息
                    with gr.Row():
                        with gr.Column():
                            self.char_name = gr.Textbox(label="角色名", interactive=False)
                            self.char_personality = gr.Textbox(label="性格", lines=2, interactive=False)
                            self.char_mood = gr.Textbox(label="当前情绪", interactive=False)
                            self.char_location = gr.Textbox(label="当前位置", interactive=False)

                        with gr.Column():
                            self.char_relationships = gr.Textbox(
                                label="人际关系",
                                lines=4,
                                interactive=False
                            )
                            self.char_goals = gr.Textbox(
                                label="当前目标",
                                lines=4,
                                interactive=False
                            )

                    # 角色历史
                    with gr.Accordion("📜 状态历史", open=False):
                        self.char_history = gr.Textbox(
                            label="历史状态",
                            lines=10,
                            interactive=False
                        )

                # Tab 2: 剧情线
                with gr.Tab("📖 剧情线"):
                    gr.Markdown("### 剧情线管理")

                    with gr.Row():
                        self.plot_thread_dropdown = gr.Dropdown(
                            label="选择剧情线",
                            choices=[],
                            value=None,
                            interactive=True
                        )
                        self.refresh_plots_btn = gr.Button("🔄 刷新", size="sm")

                    # 剧情线信息
                    with gr.Row():
                        with gr.Column():
                            self.plot_name = gr.Textbox(label="剧情线名称", interactive=False)
                            self.plot_type = gr.Textbox(label="类型", interactive=False)
                            self.plot_status = gr.Textbox(label="状态", interactive=False)
                            self.plot_description = gr.Textbox(
                                label="描述",
                                lines=3,
                                interactive=False
                            )

                        with gr.Column():
                            self.plot_events = gr.Textbox(
                                label="关键事件",
                                lines=8,
                                interactive=False
                            )

                    # 伏笔和悬念
                    with gr.Accordion("🎭 伏笔与悬念", open=False):
                        with gr.Row():
                            self.foreshadowing_list = gr.Textbox(
                                label="未解决伏笔",
                                lines=5,
                                interactive=False
                            )
                            self.cliffhangers_list = gr.Textbox(
                                label="未解决悬念",
                                lines=5,
                                interactive=False
                            )

                # Tab 3: 世界观
                with gr.Tab("🌍 世界观"):
                    gr.Markdown("### 世界观数据库")

                    with gr.Row():
                        self.world_filter = gr.Radio(
                            label="查看类型",
                            choices=["全部", "地点", "物品", "规则"],
                            value="全部",
                            interactive=True
                        )
                        self.refresh_world_btn = gr.Button("🔄 刷新", size="sm")

                    self.world_list = gr.Dropdown(
                        label="项目列表",
                        choices=[],
                        interactive=True,
                        multiselect=False
                    )

                    # 详细信息
                    self.world_detail = gr.Textbox(
                        label="详细信息",
                        lines=10,
                        interactive=False
                    )

                # Tab 4: 验证报告
                with gr.Tab("✅ 连贯性验证"):
                    gr.Markdown("### 章节连贯性验证报告")

                    with gr.Row():
                        self.validate_chapter_num = gr.Number(
                            label="章节号",
                            value=1,
                            minimum=1,
                            interactive=True
                        )
                        self.validate_btn = gr.Button("🔍 验证连贯性", variant="primary")

                    # 验证结果
                    self.validation_score = gr.Textbox(
                        label="连贯性评分",
                        interactive=False
                    )

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### ⚠️ 错误")
                            self.validation_errors = gr.Textbox(
                                label="严重问题",
                                lines=5,
                                interactive=False
                            )

                        with gr.Column():
                            gr.Markdown("#### ⚡ 警告")
                            self.validation_warnings = gr.Textbox(
                                label="警告",
                                lines=5,
                                interactive=False
                            )

                    with gr.Accordion("📊 详细报告", open=False):
                        self.validation_summary = gr.Textbox(
                            label="验证总结",
                            lines=10,
                            interactive=False
                        )

        # 绑定事件
        # 不再使用页面加载时自动刷新，因为已经在创建时加载了初始列表
        # viz_ui.load已禁用，避免刷新时choices为空导致错误

        # 项目选择器事件
        self.project_selector.change(
            fn=self.on_project_select,
            inputs=[self.project_selector],
            outputs=[
                self.project_info,
                self.character_dropdown,
                self.plot_thread_dropdown,
                self.world_list
            ]
        )

        self.refresh_projects_btn.click(
            fn=self.on_refresh_projects,
            outputs=[self.project_selector]
        )

        # 角色选择事件
        self.character_dropdown.change(
            fn=self.on_character_select,
            inputs=[self.character_dropdown],
            outputs=[
                self.char_name,
                self.char_personality,
                self.char_mood,
                self.char_location,
                self.char_relationships,
                self.char_goals,
                self.char_history
            ]
        )

        self.plot_thread_dropdown.change(
            fn=self.on_plot_select,
            inputs=[self.plot_thread_dropdown],
            outputs=[
                self.plot_name,
                self.plot_type,
                self.plot_status,
                self.plot_description,
                self.plot_events,
                self.foreshadowing_list,
                self.cliffhangers_list
            ]
        )

        self.world_list.change(
            fn=self.on_world_select,
            inputs=[self.world_list],
            outputs=[self.world_detail]
        )

        self.validate_btn.click(
            fn=self.on_validate_chapter,
            inputs=[self.validate_chapter_num],
            outputs=[
                self.validation_score,
                self.validation_errors,
                self.validation_warnings,
                self.validation_summary
            ]
        )

        return viz_ui

    def on_character_select(self, character_name: Optional[str]):
        """角色选择事件"""
        if not character_name or not self.app_state.character_tracker:
            return "", "", "", "", "", "", ""

        # 获取角色当前状态
        current_state = self.app_state.character_tracker.get_character_current_state(character_name)

        if not current_state:
            return "未找到角色", "", "", "", "", "", ""

        # 构建人际关系文本
        relationships = current_state.relationships or {}
        rel_text = "\n".join([f"{k}: {v}" for k, v in relationships.items()])

        # 构建目标文本
        goals = current_state.goals or []
        goals_text = "\n".join(goals) if goals else "无"

        # 获取历史
        history = self.app_state.character_tracker.get_character_history(character_name)
        history_text = "\n\n".join([
            f"第{state.chapter_num}章: {state.personality}, {state.mood}, 位置:{state.location}"
            for state in history[-5:]  # 最近5条
        ])

        return (
            current_state.name,
            current_state.personality,
            current_state.mood,
            current_state.location,
            rel_text,
            goals_text,
            history_text
        )

    def on_plot_select(self, thread_id: Optional[str]):
        """剧情线选择事件"""
        if not thread_id or not self.app_state.plot_manager:
            return "", "", "", "", "", "", ""

        # 获取剧情线
        thread = self.app_state.plot_manager.plot_threads.get(thread_id)

        if not thread:
            return "", "", "", "", "", "", ""

        # 获取事件
        events = thread.key_events or []
        events_text = "\n".join([
            f"第{event.chapter_num}章: {event.description}"
            for event in events[-10:]  # 最近10个
        ])

        # 获取伏笔
        foreshadowing = self.app_state.plot_manager.get_unresolved_foreshadowing(thread_id)
        foreshadowing_text = "\n".join(foreshadowing[:5]) if foreshadowing else "无"

        # 获取悬念
        cliffhangers = self.app_state.plot_manager.get_unresolved_cliffhangers(thread_id)
        cliffhangers_text = "\n".join(cliffhangers[:5]) if cliffhangers else "无"

        return (
            thread.name,
            thread.plot_type,
            thread.status,
            thread.description,
            events_text,
            foreshadowing_text,
            cliffhangers_text
        )

    def on_world_select(self, item_name: Optional[str]):
        """世界观项目选择事件"""
        if not item_name or not self.app_state.world_db:
            return ""

        # 构建详细信息
        detail_parts = []

        # 检查是否为地点
        if item_name in self.app_state.world_db.locations:
            loc = self.app_state.world_db.locations[item_name]
            detail_parts.append(f"【地点】{loc.name}")
            detail_parts.append(f"类型: {loc.type}")
            detail_parts.append(f"描述: {loc.description}")
            if loc.features:
                detail_parts.append(f"特征: {', '.join(loc.features)}")
            if loc.related_locations:
                detail_parts.append(f"相关地点: {', '.join(loc.related_locations)}")

        # 检查是否为物品
        elif item_name in self.app_state.world_db.items:
            item = self.app_state.world_db.items[item_name]
            detail_parts.append(f"【物品】{item.name}")
            detail_parts.append(f"类型: {item.type}")
            detail_parts.append(f"描述: {item.description}")
            if item.powers:
                detail_parts.append(f"能力: {', '.join(item.powers)}")
            if item.owner:
                detail_parts.append(f"持有者: {item.owner}")
            if item.location:
                detail_parts.append(f"位置: {item.location}")

        return "\n".join(detail_parts) if detail_parts else "未找到详细信息"

    def on_validate_chapter(self, chapter_num: int):
        """验证章节连贯性"""
        if not self.app_state.api_client:
            return "错误：API客户端未初始化", "", "", ""

        # 获取章节内容
        chapters = self.app_state.current_project_data.get("chapters", [])
        chapter = next((ch for ch in chapters if ch["num"] == chapter_num), None)

        if not chapter or not chapter.get("content"):
            return "错误：未找到章节内容", "", "", ""

        try:
            from src.core.coherence import validate_chapter_coherence

            result = validate_chapter_coherence(
                chapter_content=chapter["content"],
                chapter_num=chapter_num,
                chapter_outline=chapter.get("desc", ""),
                character_tracker=self.app_state.character_tracker,
                plot_manager=self.app_state.plot_manager,
                world_db=self.app_state.world_db,
                api_client=self.app_state.api_client
            )

            # 分类问题
            errors = [i.description for i in result.issues if i.severity == "error"]
            warnings = [i.description for i in result.issues if i.severity == "warning"]

            return (
                f"{result.score:.1f}/100",
                "\n".join(errors) if errors else "无错误",
                "\n".join(warnings) if warnings else "无警告",
                result.summary
            )

        except Exception as e:
            return f"验证失败: {str(e)}", "", "", ""

    def update_character_list(self):
        """更新角色列表"""
        logger = __import__("logging").getLogger(__name__)

        if not self.app_state.character_tracker:
            logger.warning("[连贯性分析] character_tracker未初始化")
            return []

        try:
            characters = list(self.app_state.character_tracker.all_characters)
            logger.info(f"[连贯性分析] 角色列表: {len(characters)} 个角色")
            return characters if characters else []
        except Exception as e:
            logger.error(f"[连贯性分析] 获取角色列表失败: {e}")
            return []

    def update_plot_list(self):
        """更新剧情线列表"""
        logger = __import__("logging").getLogger(__name__)

        if not self.app_state.plot_manager:
            logger.warning("[连贯性分析] plot_manager未初始化")
            return []

        try:
            threads = [
                f"{thread_id}: {thread.name}"
                for thread_id, thread in self.app_state.plot_manager.plot_threads.items()
            ]
            logger.info(f"[连贯性分析] 剧情线列表: {len(threads)} 条线")
            return threads if threads else []
        except Exception as e:
            logger.error(f"[连贯性分析] 获取剧情线列表失败: {e}")
            return []

    def update_world_list(self, filter_type: str = "全部"):
        """更新世界观列表"""
        items = []

        if not self.app_state.world_db:
            logger = __import__("logging").getLogger(__name__)
            logger.warning("[连贯性分析] world_db未初始化")
            return []

        try:
            if filter_type in ["全部", "地点"]:
                items.extend([f"📍 {name}" for name in self.app_state.world_db.locations.keys()])

            if filter_type in ["全部", "物品"]:
                items.extend([f"🎨 {name}" for name in self.app_state.world_db.items.keys()])

            if filter_type in ["全部", "规则"]:
                items.extend([f"📜 {name}" for name in self.app_state.world_db.rules.keys()])
        except Exception as e:
            logger = __import__("logging").getLogger(__name__)
            logger.error(f"[连贯性分析] 更新世界观列表失败: {e}")
            return []

        return items if items else []

    def _load_initial_projects(self):
        """加载初始项目列表（在UI创建时调用）"""
        projects = []
        project_dir = self.app_state.project_dir

        if project_dir.exists():
            for project_file in project_dir.glob("*.json"):
                try:
                    with open(project_file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        project_id = project_file.stem
                        title = project_data.get("title", "未命名项目")
                        # 使用简单字符串格式: "标题 (项目ID)"
                        projects.append(f"{title} ({project_id})")
                except Exception:
                    continue

        return projects

    def on_refresh_projects(self):
        """刷新项目列表"""
        projects = []
        project_dir = self.app_state.project_dir
        logger = __import__("logging").getLogger(__name__)

        if project_dir.exists():
            for project_file in project_dir.glob("*.json"):
                try:
                    with open(project_file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        project_id = project_file.stem
                        title = project_data.get("title", "未命名项目")
                        # 使用简单字符串格式: "标题 (项目ID)"
                        projects.append(f"{title} ({project_id})")
                except Exception as e:
                    logger.warning(f"读取项目文件失败 {project_file}: {e}")
                    continue

        # 始终返回value=None，避免value不在choices中的错误
        logger.info(f"[连贯性分析] 刷新项目列表: {len(projects)} 个项目")
        return gr.update(choices=projects, value=None)

    def on_project_select(self, project_selection: str):
        """项目选择事件"""
        logger = __import__("logging").getLogger(__name__)

        if not project_selection or not project_selection.strip():
            return "**请选择一个项目**", gr.update(choices=[], value=None), gr.update(choices=[], value=None), gr.update(choices=[], value=None)

        # 从字符串 "标题 (项目ID)" 中提取项目ID
        # 格式: "星河彼岸中 (20260210-215428)"
        try:
            if "(" in project_selection and ")" in project_selection:
                # 提取括号中的项目ID
                project_id = project_selection.split("(")[-1].split(")")[0].strip()
            else:
                # 如果格式不对，直接使用整个字符串作为ID
                project_id = project_selection.strip()
        except Exception:
            logger.error(f"[连贯性分析] 无法解析项目选择: {project_selection}")
            return f"❌ 无法解析项目选择: {project_selection}", gr.update(choices=[], value=None), gr.update(choices=[], value=None), gr.update(choices=[], value=None)

        logger.info(f"[连贯性分析] 选择项目: {project_selection} -> 项目ID: {project_id}")

        # 加载项目数据
        project_file = self.app_state.project_dir / f"{project_id}.json"
        if not project_file.exists():
            logger.error(f"[连贯性分析] 项目文件不存在: {project_file}")
            return f"❌ 项目文件不存在: {project_id}", gr.update(choices=[], value=None), gr.update(choices=[], value=None), gr.update(choices=[], value=None)

        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # 更新当前项目
            self.app_state.current_project_id = project_id
            self.app_state.current_project_data = project_data

            # 初始化该项目的连贯性系统
            self.app_state.init_coherence_systems(project_id)

            # 构建项目信息
            title = project_data.get("title", "未命名项目")
            genre = project_data.get("genre", "")
            total_chapters = len(project_data.get("chapters", []))
            created_at = project_data.get("created_at", "")

            info = f"""### 📖 {title}

**类型**: {genre}
**章节数**: {total_chapters}
**项目ID**: `{project_id}`
**创建时间**: {created_at}

---

✅ 已加载该项目的连贯性数据（角色、剧情线、世界观）
"""

            # 更新各个下拉框，使用gr.update()而不是直接返回列表
            character_choices = self.update_character_list()
            plot_choices = self.update_plot_list()
            world_choices = self.update_world_list()

            logger.info(f"[连贯性分析] 角色数: {len(character_choices)}, 剧情线数: {len(plot_choices)}, 世界观项数: {len(world_choices)}")

            return info, gr.update(choices=character_choices, value=None), gr.update(choices=plot_choices, value=None), gr.update(choices=world_choices, value=None)

        except Exception as e:
            logger.error(f"[连贯性分析] 加载项目失败: {e}", exc_info=True)
            error_msg = f"❌ 加载项目失败: {str(e)}"
            return error_msg, gr.update(choices=[], value=None), gr.update(choices=[], value=None), gr.update(choices=[], value=None)
