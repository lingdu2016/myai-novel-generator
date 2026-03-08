"""
批量生成功能模块
支持批量生成多个章节，提升创作效率

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
"""

import gradio as gr
import logging
from typing import List, Tuple, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def create_batch_generation_ui(app_state):
    """
    创建批量生成UI

    Args:
        app_state: 应用状态对象

    Returns:
        Gradio Blocks对象
    """
    with gr.Blocks() as batch_ui:
        gr.Markdown("## 🚀 批量生成章节")
        gr.Markdown("### 一次性生成多个章节，大幅提升创作效率")

        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 📋 章节配置")

                # 章节标题输入
                chapter_titles_input = gr.Textbox(
                    label="章节标题列表",
                    lines=20,
                    placeholder="请输入章节标题，每行一个，例如：\n第一章 系统激活\n第二章 初入江湖\n第三章 遭遇强敌\n...",
                    info="支持手动输入或从大纲生成"
                )

                # 快捷操作
                with gr.Row():
                    clear_titles_btn = gr.Button("🗑️ 清空", size="sm")
                    example_titles_btn = gr.Button("📝 示例模板", size="sm")

                # 生成参数
                with gr.Accordion("⚙️ 生成参数", open=False):
                    batch_target_words = gr.Number(
                        label="每章目标字数",
                        value=2000,
                        minimum=100,
                        maximum=50000
                    )

                    batch_delay = gr.Number(
                        label="生成间隔（秒）",
                        value=2,
                        minimum=0,
                        maximum=60,
                        info="每章生成之间的等待时间，避免API限流"
                    )

                    batch_auto_save = gr.Checkbox(
                        label="每章自动保存",
                        value=True,
                        info="生成完一章后自动保存，防止数据丢失"
                    )

                # 生成控制
                with gr.Row():
                    start_chapter_num = gr.Number(
                        label="起始章节号",
                        value=1,
                        minimum=1,
                        maximum=10000
                    )

                    stop_condition = gr.Textbox(
                        label="停止条件（可选）",
                        placeholder="例如：第10章、遇到特定情节等",
                        info="满足条件后自动停止生成"
                    )

            with gr.Column(scale=1):
                gr.Markdown("### 📊 生成进度")

                # 进度显示
                batch_progress = gr.Textbox(
                    label="生成进度",
                    value="等待开始...",
                    interactive=False,
                    lines=3
                )

                batch_progress_bar = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=0,
                    label="完成度",
                    interactive=False
                )

                # 操作按钮
                with gr.Row():
                    batch_start_btn = gr.Button("🚀 开始批量生成", variant="primary", size="lg")
                    batch_pause_btn = gr.Button("⏸️ 暂停生成", variant="stop", size="lg")
                    batch_stop_btn = gr.Button("⏹️ 停止生成", variant="stop", size="lg")

                # 生成结果
                batch_results = gr.Textbox(
                    label="生成结果",
                    lines=15,
                    interactive=False,
                    info="显示每章的生成状态"
                )

                # 导出结果
                with gr.Row():
                    export_results_btn = gr.Button("📤 导出所有章节", variant="secondary")
                    copy_results_btn = gr.Button("📋 复制结果")

        # 事件处理
        def on_load_example():
            """加载示例模板"""
            examples = [
                "第一章 序幕拉开",
                "第二章 少年初醒",
                "第三章 家族测试",
                "第四章 惊艳四座",
                "第五章 拜入宗门",
                "第六章 外门弟子",
                "第七章 初次修炼",
                "第八章 宗门大比",
                "第九章 意外夺冠",
                "第十章 遭遇暗算",
                "第十一章 绝境求生",
                "第十二章 奇遇机缘",
                "第十三章 实力大增",
                "第十四章 反击开始",
                "第十五章 一雪前耻"
            ]
            return "\n".join(examples)

        def on_parse_titles(titles_text):
            """解析章节标题"""
            if not titles_text or not titles_text.strip():
                return []

            lines = titles_text.strip().split('\n')
            titles = [line.strip() for line in lines if line.strip()]
            logger.debug(f"[批量生成] 解析章节标题，识别到 {len(titles)} 个章节")
            return titles

        def on_start_batch_generation(titles_text, start_num, target_words, delay, auto_save, stop_cond):
            """开始批量生成"""
            logger.info(f"[批量生成] 开始批量生成，起始章节: {start_num}, 目标字数: {target_words}, 间隔: {delay}秒")

            titles = on_parse_titles(titles_text)
            if not titles:
                logger.warning("[批量生成] 没有有效的章节标题")
                return "❌ 请先输入章节标题", 0, "没有可生成的章节"

            total_chapters = len(titles)
            results = []
            progress_info = []

            progress_info.append(f"准备生成 {total_chapters} 个章节...")
            logger.info(f"[批量生成] 准备生成 {total_chapters} 个章节")

            # TODO: 实现实际的批量生成逻辑
            # 这里需要调用app_state的生成函数

            for i, title in enumerate(titles):
                chapter_num = int(start_num) + i
                progress_info.append(f"第 {i+1}/{total_chapters} 章: {title}")
                results.append(f"第{chapter_num}章 {title} - 待生成")

            logger.info(f"[批量生成] 批量生成计划完成，共 {total_chapters} 章")
            return (
                "\n".join(progress_info),
                100,  # 完成度
                "\n".join(results)
            )

        # 绑定事件
        clear_titles_btn.click(
            fn=lambda: "",
            outputs=[chapter_titles_input]
        )

        example_titles_btn.click(
            fn=on_load_example,
            outputs=[chapter_titles_input]
        )

        batch_start_btn.click(
            fn=on_start_batch_generation,
            inputs=[
                chapter_titles_input,
                start_chapter_num,
                batch_target_words,
                batch_delay,
                batch_auto_save,
                stop_condition
            ],
            outputs=[
                batch_progress,
                batch_progress_bar,
                batch_results
            ]
        )

        batch_pause_btn.click(
            fn=lambda: "批量生成已暂停（功能开发中）",
            outputs=[batch_results]
        )

        batch_stop_btn.click(
            fn=lambda: "批量生成已停止",
            outputs=[batch_results]
        )

    return batch_ui
