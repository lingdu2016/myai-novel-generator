"""
项目提示词编辑器

功能：
1. 管理项目所有提示词
2. 支持预设模板和自定义模板
3. 实时编辑和保存
4. 导入/导出配置

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import gradio as gr
import logging
from typing import Dict, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def create_project_prompt_editor(
    app_state,
    prompt_manager
):
    """
    创建项目提示词编辑器
    
    Args:
        app_state: 应用状态
        prompt_manager: 提示词管理器
        
    Returns:
        Gradio组件
    """
    
    with gr.Column() as prompt_editor:
        gr.Markdown("## 📝 项目提示词编辑器")
        gr.Markdown("管理项目所有提示词，支持实时编辑和保存")
        
        # ========== 提示词分类 ==========
        with gr.Row():
            with gr.Column(scale=1):
                prompt_category = gr.Radio(
                    choices=[
                        "📖 章节生成",
                        "✏️ 内容重写",
                        "📋 大纲生成",
                        "🎭 角色提取",
                        "📊 剧情分析",
                        "🌍 世界观构建",
                        "💬 对话优化",
                        "🎨 风格调整"
                    ],
                    value="📖 章节生成",
                    label="提示词分类",
                    info="选择要编辑的提示词类型"
                )
            
            with gr.Column(scale=2):
                prompt_selector = gr.Dropdown(
                    choices=[],
                    label="选择提示词",
                    info="从列表中选择或创建新提示词",
                    interactive=True,
                    allow_custom_value=True
                )
        
        # ========== 提示词编辑区 ==========
        gr.Markdown("### ✏️ 编辑提示词")
        
        with gr.Row():
            with gr.Column(scale=3):
                prompt_content = gr.Textbox(
                    label="提示词内容",
                    lines=20,
                    placeholder="在此编辑提示词内容...",
                    interactive=True,
                    show_copy_button=True
                )
            
            with gr.Column(scale=1):
                # 变量说明
                gr.Markdown("#### 📌 可用变量")
                variables_info = gr.Markdown("""
**通用变量：**
- `{title}` - 小说标题
- `{genre}` - 小说类型
- `{chapter_num}` - 章节号
- `{chapter_title}` - 章节标题

**章节生成：**
- `{chapter_desc}` - 章节描述
- `{context}` - 前文回顾
- `{target_words}` - 目标字数
- `{characters}` - 角色信息

**大纲生成：**
- `{total_chapters}` - 总章节数
- `{character_setting}` - 角色设定
- `{world_setting}` - 世界观设定
- `{plot_idea}` - 剧情构思

**重写/润色：**
- `{content}` - 原始内容
- `{style}` - 目标风格
- `{issues}` - 问题列表
""")
        
        # ========== 预设模板库 ==========
        with gr.Accordion("📚 预设模板库", open=False):
            gr.Markdown("选择预设模板快速开始")
            
            with gr.Row():
                preset_category = gr.Dropdown(
                    choices=[
                        "重写风格",
                        "大纲生成",
                        "角色提取",
                        "剧情分析"
                    ],
                    label="模板类别",
                    value="重写风格"
                )
                
                preset_selector = gr.Dropdown(
                    choices=[],
                    label="预设模板",
                    interactive=True
                )
            
            preset_preview = gr.Textbox(
                label="模板预览",
                lines=10,
                interactive=False
            )
            
            use_preset_btn = gr.Button("✨ 使用此模板", variant="secondary")
        
        # ========== 操作按钮 ==========
        gr.Markdown("### 🔧 操作")
        
        with gr.Row():
            save_btn = gr.Button("💾 保存提示词", variant="primary", size="lg")
            save_as_btn = gr.Button("💾 另存为...", variant="secondary", size="lg")
            reset_btn = gr.Button("🔄 重置为预设", variant="secondary", size="lg")
            delete_btn = gr.Button("🗑️ 删除", variant="stop", size="lg")
        
        with gr.Row():
            export_btn = gr.Button("📤 导出所有提示词", variant="secondary")
            import_btn = gr.Button("📥 导入提示词配置", variant="secondary")
            preview_btn = gr.Button("👁️ 预览效果", variant="secondary")
        
        # ========== 状态输出 ==========
        status_output = gr.Textbox(
            label="操作状态",
            lines=3,
            interactive=False,
            show_copy_button=True
        )
        
        # ========== 预览输出 ==========
        with gr.Accordion("🔍 预览效果", open=False):
            preview_output = gr.Textbox(
                label="预览结果",
                lines=15,
                interactive=False
            )
        
        # ========== 事件处理函数 ==========
        
        def on_category_change(category):
            """分类切换时更新提示词列表"""
            try:
                # 映射分类名称
                category_map = {
                    "📖 章节生成": "generation",
                    "✏️ 内容重写": "rewrite",
                    "📋 大纲生成": "outline",
                    "🎭 角色提取": "character",
                    "📊 剧情分析": "plot",
                    "🌍 世界观构建": "world",
                    "💬 对话优化": "dialogue",
                    "🎨 风格调整": "style"
                }
                
                internal_category = category_map.get(category, "generation")
                
                # 获取该分类下的所有提示词
                templates = prompt_manager.list_templates(internal_category)
                
                # 构建选项列表
                choices = []
                for cat, names in templates.items():
                    for name in names:
                        choices.append(f"{name}")
                
                # 添加"创建新提示词"选项
                choices.insert(0, "➕ 创建新提示词")
                
                return gr.Dropdown(choices=choices, value=choices[0] if choices else None)
                
            except Exception as e:
                logger.error(f"更新提示词列表失败: {e}", exc_info=True)
                return gr.Dropdown(choices=[])
        
        def on_prompt_select(category, prompt_name):
            """选择提示词时加载内容"""
            try:
                if not prompt_name or prompt_name == "➕ 创建新提示词":
                    return "", "准备创建新提示词"
                
                # 映射分类名称
                category_map = {
                    "📖 章节生成": "generation",
                    "✏️ 内容重写": "rewrite",
                    "📋 大纲生成": "outline",
                    "🎭 角色提取": "character",
                    "📊 剧情分析": "plot",
                    "🌍 世界观构建": "world",
                    "💬 对话优化": "dialogue",
                    "🎨 风格调整": "style"
                }
                
                internal_category = category_map.get(category, "generation")
                
                # 获取提示词内容
                content = prompt_manager.get_template(internal_category, prompt_name)
                
                if content:
                    return content, f"✓ 已加载提示词: {prompt_name}"
                else:
                    return "", f"✗ 未找到提示词: {prompt_name}"
                    
            except Exception as e:
                logger.error(f"加载提示词失败: {e}", exc_info=True)
                return "", f"✗ 加载失败: {str(e)}"
        
        def on_save_prompt(category, prompt_name, content):
            """保存提示词"""
            try:
                if not prompt_name or prompt_name == "➕ 创建新提示词":
                    return "✗ 请输入提示词名称"
                
                if not content or not content.strip():
                    return "✗ 提示词内容不能为空"
                
                # 映射分类名称
                category_map = {
                    "📖 章节生成": "generation",
                    "✏️ 内容重写": "rewrite",
                    "📋 大纲生成": "outline",
                    "🎭 角色提取": "character",
                    "📊 剧情分析": "plot",
                    "🌍 世界观构建": "world",
                    "💬 对话优化": "dialogue",
                    "🎨 风格调整": "style"
                }
                
                internal_category = category_map.get(category, "generation")
                
                # 保存提示词
                prompt_manager.set_template(internal_category, prompt_name, content)
                
                # 保存到文件
                prompt_manager.save_custom_templates()
                
                return f"✓ 提示词已保存: {category} > {prompt_name}"
                
            except Exception as e:
                logger.error(f"保存提示词失败: {e}", exc_info=True)
                return f"✗ 保存失败: {str(e)}"
        
        def on_save_as(category, new_name, content):
            """另存为"""
            try:
                if not new_name or not new_name.strip():
                    return "✗ 请输入新名称", gr.Dropdown()
                
                if not content or not content.strip():
                    return "✗ 提示词内容不能为空", gr.Dropdown()
                
                # 映射分类名称
                category_map = {
                    "📖 章节生成": "generation",
                    "✏️ 内容重写": "rewrite",
                    "📋 大纲生成": "outline",
                    "🎭 角色提取": "character",
                    "📊 剧情分析": "plot",
                    "🌍 世界观构建": "world",
                    "💬 对话优化": "dialogue",
                    "🎨 风格调整": "style"
                }
                
                internal_category = category_map.get(category, "generation")
                
                # 保存提示词
                prompt_manager.set_template(internal_category, new_name.strip(), content)
                
                # 保存到文件
                prompt_manager.save_custom_templates()
                
                # 更新下拉列表
                templates = prompt_manager.list_templates(internal_category)
                choices = []
                for cat, names in templates.items():
                    for name in names:
                        choices.append(f"{name}")
                
                return f"✓ 已另存为: {new_name}", gr.Dropdown(choices=choices, value=new_name)
                
            except Exception as e:
                logger.error(f"另存为失败: {e}", exc_info=True)
                return f"✗ 另存为失败: {str(e)}", gr.Dropdown()
        
        def on_reset(category, prompt_name):
            """重置为预设"""
            try:
                # 映射分类名称
                category_map = {
                    "📖 章节生成": "generation",
                    "✏️ 内容重写": "rewrite",
                    "📋 大纲生成": "outline",
                    "🎭 角色提取": "character",
                    "📊 剧情分析": "plot",
                    "🌍 世界观构建": "world",
                    "💬 对话优化": "dialogue",
                    "🎨 风格调整": "style"
                }
                
                internal_category = category_map.get(category, "generation")
                
                # 重置为预设
                success = prompt_manager.reset_to_preset(internal_category, prompt_name)
                
                if success:
                    content = prompt_manager.get_template(internal_category, prompt_name, use_preset=True)
                    return content, f"✓ 已重置为预设: {prompt_name}"
                else:
                    return "", f"✗ 未找到预设: {prompt_name}"
                    
            except Exception as e:
                logger.error(f"重置失败: {e}", exc_info=True)
                return "", f"✗ 重置失败: {str(e)}"
        
        def on_delete(category, prompt_name):
            """删除提示词"""
            try:
                if not prompt_name or prompt_name == "➕ 创建新提示词":
                    return "✗ 请选择要删除的提示词", gr.Dropdown()
                
                # 映射分类名称
                category_map = {
                    "📖 章节生成": "generation",
                    "✏️ 内容重写": "rewrite",
                    "📋 大纲生成": "outline",
                    "🎭 角色提取": "character",
                    "📊 剧情分析": "plot",
                    "🌍 世界观构建": "world",
                    "💬 对话优化": "dialogue",
                    "🎨 风格调整": "style"
                }
                
                internal_category = category_map.get(category, "generation")
                
                # 删除提示词
                success = prompt_manager.delete_template(internal_category, prompt_name)
                
                if success:
                    # 保存到文件
                    prompt_manager.save_custom_templates()
                    
                    # 更新下拉列表
                    templates = prompt_manager.list_templates(internal_category)
                    choices = []
                    for cat, names in templates.items():
                        for name in names:
                            choices.append(f"{name}")
                    choices.insert(0, "➕ 创建新提示词")
                    
                    return f"✓ 已删除: {prompt_name}", gr.Dropdown(choices=choices, value=choices[0] if choices else None)
                else:
                    return f"✗ 删除失败: 未找到 {prompt_name}", gr.Dropdown()
                    
            except Exception as e:
                logger.error(f"删除失败: {e}", exc_info=True)
                return f"✗ 删除失败: {str(e)}", gr.Dropdown()
        
        def on_export():
            """导出所有提示词"""
            try:
                export_data = prompt_manager.export_all()
                
                # 保存到文件
                export_file = Path("config/prompts_export.json")
                export_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                return f"✓ 已导出到: {export_file}"
                
            except Exception as e:
                logger.error(f"导出失败: {e}", exc_info=True)
                return f"✗ 导出失败: {str(e)}"
        
        def on_import(file):
            """导入提示词配置"""
            try:
                if not file:
                    return "✗ 请选择要导入的文件"
                
                with open(file, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                # 导入提示词
                count = prompt_manager.import_all(import_data)
                
                # 保存到文件
                prompt_manager.save_custom_templates()
                
                return f"✓ 已导入 {count} 个提示词"
                
            except Exception as e:
                logger.error(f"导入失败: {e}", exc_info=True)
                return f"✗ 导入失败: {str(e)}"
        
        def on_preset_category_change(category):
            """预设分类切换"""
            try:
                # 获取预设模板列表
                from src.core.prompts.templates import PRESET_TEMPLATES
                
                choices = []
                for key in PRESET_TEMPLATES.keys():
                    if category in key:
                        choices.append(key)
                
                return gr.Dropdown(choices=choices, value=choices[0] if choices else None)
                
            except Exception as e:
                logger.error(f"更新预设列表失败: {e}", exc_info=True)
                return gr.Dropdown(choices=[])
        
        def on_preset_select(preset_name):
            """选择预设模板"""
            try:
                from src.core.prompts.templates import PRESET_TEMPLATES
                
                if preset_name and preset_name in PRESET_TEMPLATES:
                    return PRESET_TEMPLATES[preset_name]
                return ""
                
            except Exception as e:
                logger.error(f"加载预设失败: {e}", exc_info=True)
                return ""
        
        def on_use_preset(preset_content):
            """使用预设模板"""
            return preset_content, "✓ 已加载预设模板，可以编辑后保存"
        
        # ========== 绑定事件 ==========
        
        prompt_category.change(
            fn=on_category_change,
            inputs=[prompt_category],
            outputs=[prompt_selector]
        )
        
        prompt_selector.change(
            fn=on_prompt_select,
            inputs=[prompt_category, prompt_selector],
            outputs=[prompt_content, status_output]
        )
        
        save_btn.click(
            fn=on_save_prompt,
            inputs=[prompt_category, prompt_selector, prompt_content],
            outputs=[status_output]
        )
        
        reset_btn.click(
            fn=on_reset,
            inputs=[prompt_category, prompt_selector],
            outputs=[prompt_content, status_output]
        )
        
        delete_btn.click(
            fn=on_delete,
            inputs=[prompt_category, prompt_selector],
            outputs=[status_output, prompt_selector]
        )
        
        export_btn.click(
            fn=on_export,
            outputs=[status_output]
        )
        
        import_btn.click(
            fn=on_import,
            outputs=[status_output]
        )
        
        preset_category.change(
            fn=on_preset_category_change,
            inputs=[preset_category],
            outputs=[preset_selector]
        )
        
        preset_selector.change(
            fn=on_preset_select,
            inputs=[preset_selector],
            outputs=[preset_preview]
        )
        
        use_preset_btn.click(
            fn=on_use_preset,
            inputs=[preset_preview],
            outputs=[prompt_content, status_output]
        )
    
    return prompt_editor
