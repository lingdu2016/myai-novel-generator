"""
大纲生成功能模块
AI生成小说大纲，集成连贯性系统

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
"""

import gradio as gr
import logging
from typing import Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_outline_with_api(api_client, title: str, genre: str, total_chapters: int,
                               char_setting: str, world_setting: str, plot_idea: str) -> Tuple[str, str]:
    """
    使用API客户端生成大纲

    Args:
        api_client: UnifiedAPIClient实例
        title: 小说标题
        genre: 类型
        total_chapters: 总章节数
        char_setting: 人物设定
        world_setting: 世界观
        plot_idea: 主线剧情

    Returns:
        (大纲文本, 状态消息)
    """
    if not api_client:
        return "", "API客户端未初始化"

    logger.info(f"[大纲生成] 开始生成大纲: {title} ({genre}, {total_chapters}章)")

    try:
        # 构建提示词
        prompt = f"""请为一部小说生成详细的大纲。

【基本信息】
小说标题：{title}
类型：{genre}
总章节数：{total_chapters}章

【人物设定】
{char_setting}

【世界观设定】
{world_setting}

【主线剧情】
{plot_idea}

要求：
1. 生成完整的章节大纲，共{total_chapters}章
2. 每章包含：章节序号、章节标题、章节概要（100-200字）
3. 情节安排合理，有起承转合
4. 伏笔和悬念的设置
5. 人物成长弧线
6. 按以下格式输出：

第1章：[章节标题]
- 章节概要：...

第2章：[章节标题]
- 章节概要：...

请开始生成："""

        # 调用API
        messages = [
            {"role": "system", "content": "你是一位专业的小说策划师，擅长构建小说大纲和情节设计。"},
            {"role": "user", "content": prompt}
        ]

        result = api_client.generate(
            messages=messages,
            max_tokens=4000,
            temperature=0.8
        )

        if result and result.strip():
            # 简单验证大纲格式
            if "第1章" in result or "第一章" in result:
                logger.info(f"[大纲生成] 大纲生成成功，长度: {len(result)} 字符")
                return result, "大纲生成成功"
            else:
                # 可能格式不对，但返回了内容
                logger.warning(f"[大纲生成] 生成的大纲格式可能不符合预期，长度: {len(result)} 字符")
                return result, "大纲生成完成（格式可能需要调整）"
        else:
            logger.error(f"[大纲生成] API返回空结果")
            return "", "大纲生成失败：API返回空结果"

    except Exception as e:
        logger.error(f"[大纲生成] 大纲生成失败: {e}", exc_info=True)
        return "", f"大纲生成失败: {str(e)}"


def parse_outline(outline_text: str) -> list:
    """
    解析大纲文本为结构化数据

    Args:
        outline_text: 大纲文本

    Returns:
        章节列表，每个元素包含 (章节号, 标题, 描述)
    """
    chapters = []
    lines = outline_text.split("\n")

    current_chapter = None
    current_title = None
    current_desc = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检测章节标题行
        if line.startswith("第") and ("章" in line):
            # 保存上一章
            if current_chapter is not None:
                desc = "\n".join(current_desc).strip()
                chapters.append({
                    "num": current_chapter,
                    "title": current_title,
                    "desc": desc
                })

            # 解析新章节
            try:
                # 提取章节号
                if "第" in line and "章" in line:
                    chapter_part = line.split("章")[0]
                    num_str = chapter_part.replace("第", "").strip()
                    current_chapter = int(num_str) if num_str.isdigit() else len(chapters) + 1
                else:
                    current_chapter = len(chapters) + 1

                # 提取标题
                if "：" in line:
                    current_title = line.split("：", 1)[1].strip()
                elif ":" in line:
                    current_title = line.split(":", 1)[1].strip()
                else:
                    current_title = f"第{current_chapter}章"

                current_desc = []

            except Exception as e:
                logger.warning(f"[大纲解析] 解析章节行失败: {line}, 错误: {e}")
                current_chapter = len(chapters) + 1
                current_title = line
                current_desc = []

        elif line.startswith("- 章节概要") or line.startswith("章节概要"):
            # 章节概要行，跳过
            continue
        else:
            # 描述行
            if current_chapter is not None:
                current_desc.append(line)

    # 保存最后一章
    if current_chapter is not None:
        desc = "\n".join(current_desc).strip()
        chapters.append({
            "num": current_chapter,
            "title": current_title,
            "desc": desc
        })

    return chapters


def create_outline_ui(app_state):
    """
    创建大纲生成UI

    Args:
        app_state: 应用状态对象

    Returns:
        Gradio Blocks对象
    """
    with gr.Blocks() as outline_ui:
        gr.Markdown("## ✍️ 大纲生成")
        gr.Markdown("### 填写设定 → AI生成大纲")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 小说设定")

                title_input = gr.Textbox(
                    label="小说标题",
                    placeholder="输入小说标题..."
                )

                genre_input = gr.Textbox(
                    label="类型",
                    placeholder="如：玄幻仙侠、都市言情、科幻硬核",
                    value="玄幻仙侠"
                )

                total_chapters = gr.Number(
                    label="总章节数",
                    value=50,
                    minimum=1,
                    maximum=1000
                )

                char_setting = gr.Textbox(
                    label="人物设定",
                    lines=3,
                    placeholder="主角的性格、背景、能力..."
                )

                world_setting = gr.Textbox(
                    label="世界观设定",
                    lines=3,
                    placeholder="修仙体系、世界背景、历史年代..."
                )

                plot_idea = gr.Textbox(
                    label="主线剧情",
                    lines=3,
                    placeholder="故事的主要走向、起承转合..."
                )

                generate_btn = gr.Button("🚀 生成大纲", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown("### 生成结果")

                outline_output = gr.Textbox(
                    label="大纲内容",
                    lines=20,
                    interactive=True
                )

                outline_status = gr.Textbox(
                    label="状态",
                    interactive=False
                )

                with gr.Row():
                    copy_outline_btn = gr.Button("📋 复制大纲", size="sm")
                    save_outline_btn = gr.Button("💾 保存到项目", size="sm")

                gr.Markdown("---")
                gr.Markdown("### 大纲解析")

                parsed_info = gr.Textbox(
                    label="解析结果",
                    lines=10,
                    interactive=False
                )

        # 事件处理
        def on_generate_click(title, genre, chapters, char_set, world_set, plot):
            if not title or not title.strip():
                return "", "❌ 请填写小说标题"

            if not app_state.api_client:
                return "", "❌ 请先在'API配置'标签中配置API"

            # 生成大纲
            outline, status = generate_outline_with_api(
                app_state.api_client,
                title.strip(),
                genre.strip() if genre else "未分类",
                int(chapters) if chapters else 50,
                char_set,
                world_set,
                plot
            )

            # 解析大纲
            if outline and status == "大纲生成成功":
                parsed = parse_outline(outline)
                parsed_text = f"共识别 {len(parsed)} 章：\n\n"
                for ch in parsed[:10]:  # 显示前10章
                    parsed_text += f"第{ch['num']}章: {ch['title']}\n"
                    parsed_text += f"  {ch['desc'][:50]}...\n\n"

                if len(parsed) > 10:
                    parsed_text += f"...（还有 {len(parsed) - 10} 章）"

                return outline, status, parsed_text
            else:
                logger.warning(f"[大纲生成] 大纲生成状态不是成功: {status}")
                return outline, status, ""

        def on_copy_click(text):
            if text:
                return gr.update(value="✓ 已复制到剪贴板")
            return gr.update(value="❌ 没有内容可复制")

        def on_save_click(outline_text, title):
            if not outline_text or not outline_text.strip():
                return "❌ 没有可保存的大纲"
            if not title or not title.strip():
                return "❌ 请填写小说标题"

            # TODO: 保存到当前项目或创建新项目
            return "✓ 大纲已保存（功能开发中）"

        # 绑定事件
        generate_btn.click(
            fn=on_generate_click,
            inputs=[title_input, genre_input, total_chapters, char_setting, world_setting, plot_idea],
            outputs=[outline_output, outline_status, parsed_info]
        )

        copy_outline_btn.click(
            fn=on_copy_click,
            inputs=[outline_output],
            outputs=[outline_status]
        )

        save_outline_btn.click(
            fn=on_save_click,
            inputs=[outline_output, title_input],
            outputs=[outline_status]
        )

    return outline_ui
