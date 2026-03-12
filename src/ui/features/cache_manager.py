"""
缓存管理功能模块
管理生成缓存和摘要缓存，支持查看、清理、统计

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
"""

import gradio as gr
import logging
import os
from typing import Tuple, List
from pathlib import Path
from ...config.paths import get_projects_dir, get_cache_dir

logger = logging.getLogger(__name__)


def get_project_info(project_id: str) -> dict:
    """
    从项目文件中获取项目信息

    Args:
        project_id: 项目ID

    Returns:
        项目信息字典
    """
    try:
        project_file = get_projects_dir() / f"{project_id}.json"
        if project_file.exists():
            import json
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
                return {
                    "title": project_data.get("title", "未命名项目"),
                    "genre": project_data.get("genre", ""),
                    "id": project_id
                }
    except Exception as e:
        logger.warning(f"读取项目文件失败 {project_id}: {e}")

    return {
        "title": f"项目 {project_id[:8]}...",  # 使用项目ID前8位
        "genre": "",
        "id": project_id
    }


def list_generation_caches():
    """
    列出所有生成缓存

    Returns:
        缓存信息列表
    """
    try:
        from novel_generator import list_generation_caches as list_caches_func
        return list_caches_func()
    except ImportError:
        # 如果novel_generator模块不存在，手动扫描
        caches = []
        cache_dir = get_cache_dir() / "generation"
        if cache_dir.exists():
            for cache_file in cache_dir.glob("*.json"):
                try:
                    import json
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)

                        # 从文件名提取 project_id
                        project_id = cache_file.stem  # 去掉 .json 后缀

                        # 从项目文件获取项目信息
                        project_info = get_project_info(project_id)

                        caches.append({
                            "project_id": project_id,
                            "title": project_info["title"],  # 使用项目文件中的标题
                            "genre": project_info.get("genre", ""),
                            "current_chapter": cache_data.get("current_chapter", 0),
                            "total_chapters": cache_data.get("total_chapters", 0),
                            "status": cache_data.get("generation_status", "unknown"),
                            "timestamp": cache_data.get("timestamp", ""),
                            "size": os.path.getsize(cache_file)
                        })
                except Exception as e:
                    logger.warning(f"读取缓存文件失败 {cache_file}: {e}")
        return caches


def list_summary_caches():
    """
    列出所有摘要缓存

    Returns:
        摘要缓存信息列表
    """
    try:
        from novel_generator import list_summary_caches as list_caches_func
        return list_caches_func()
    except ImportError:
        # 手动扫描
        caches = []
        cache_dir = get_cache_dir() / "summaries"
        if cache_dir.exists():
            for cache_file in cache_dir.glob("*.json"):
                try:
                    import json
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        caches.append({
                            "project_id": cache_data.get("project_id", ""),
                            "count": cache_data.get("count", 0),
                            "timestamp": cache_data.get("timestamp", ""),
                            "size": os.path.getsize(cache_file)
                        })
                except Exception as e:
                    logger.warning(f"读取摘要缓存失败 {cache_file}: {e}")
        return caches


def clear_generation_cache(project_id: str) -> Tuple[bool, str]:
    """
    清理指定项目的生成缓存

    Args:
        project_id: 项目ID

    Returns:
        (成功标志, 状态信息)
    """
    try:
        from novel_generator import clear_generation_cache as clear_cache_func
        return clear_cache_func(project_id)
    except ImportError:
        # 手动删除
        cache_file = get_cache_dir() / "generation" / f"{project_id}.json"
        if cache_file.exists():
            cache_file.unlink()
            return True, f"缓存已清理: {project_id}"
        return False, f"缓存不存在: {project_id}"


def clear_all_generation_caches() -> Tuple[bool, str]:
    """
    清理所有生成缓存

    Returns:
        (成功标志, 状态信息)
    """
    try:
        from novel_generator import clear_generation_cache as clear_cache_func

        # 获取所有缓存
        caches = list_generation_caches()
        cleared = 0
        for cache in caches:
            project_id = cache.get("title", "").replace(" ", "_").replace("/", "_")
            success, _ = clear_cache_func(project_id)
            if success:
                cleared += 1

        return True, f"已清理 {cleared}/{len(caches)} 个缓存"

    except ImportError:
        # 手动清理
        cache_dir = get_cache_dir() / "generation"
        if cache_dir.exists():
            import shutil
            count = len(list(cache_dir.glob("*.json")))
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(exist_ok=True)
            return True, f"已清理 {count} 个缓存"
        return False, "没有缓存需要清理"


def get_generation_cache_size() -> str:
    """
    获取生成缓存大小

    Returns:
        缓存大小描述
    """
    try:
        from novel_generator import get_cache_size as get_size_func
        return get_size_func()
    except ImportError:
        # 手动计算
        cache_dir = get_cache_dir() / "generation"
        if cache_dir.exists():
            total_size = sum(f.stat().st_size for f in cache_dir.glob("*") if f.is_file())
            size_mb = total_size / 1024 / 1024
            return f"{size_mb:.2f} MB"
        return "0 MB"


def clear_all_summary_caches() -> Tuple[bool, str]:
    """
    清理所有摘要缓存

    Returns:
        (成功标志, 状态信息)
    """
    try:
        from novel_generator import clear_chapter_summaries as clear_summaries_func
        # 这需要项目ID，但我们可以清空整个目录
        cache_dir = get_cache_dir() / "summaries"
        if cache_dir.exists():
            import shutil
            count = len(list(cache_dir.glob("*.json")))
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(exist_ok=True)
            return True, f"已清理 {count} 个摘要缓存"
        return True, "没有摘要缓存需要清理"

    except ImportError:
        # 手动清理
        cache_dir = get_cache_dir() / "summaries"
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(exist_ok=True)
            return True, "摘要缓存已清理"
        return False, "摘要缓存清理失败"


def get_summary_cache_size() -> str:
    """
    获取摘要缓存大小

    Returns:
        缓存大小描述
    """
    try:
        from novel_generator import get_summary_cache_size as get_size_func
        return get_size_func()
    except ImportError:
        # 手动计算
        cache_dir = get_cache_dir() / "summaries"
        if cache_dir.exists():
            total_size = sum(f.stat().st_size for f in cache_dir.glob("*") if f.is_file())
            size_mb = total_size / 1024 / 1024
            return f"{size_mb:.2f} MB"
        return "0 MB"


def create_cache_manager_ui(app_state):
    """
    创建缓存管理UI

    Args:
        app_state: 应用状态对象

    Returns:
        Gradio Blocks对象
    """
    with gr.Blocks() as cache_ui:
        gr.Markdown("## 💾 缓存管理")
        gr.Markdown("### 管理生成缓存和摘要缓存，释放存储空间")

        with gr.Tabs():
            # Tab 1: 生成缓存
            with gr.Tab("📝 生成缓存"):
                gr.Markdown("#### 生成进度缓存")

                caches_table = gr.Dataframe(
                    headers=["项目ID", "项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"],
                    interactive=False
                )

                with gr.Row():
                    refresh_caches_btn = gr.Button("🔄 刷新列表", size="sm")
                    cache_size_info = gr.Textbox(label="缓存大小", interactive=False, lines=1)

                with gr.Row():
                    clear_cache_btn = gr.Button("🗑️ 清理选中缓存", variant="stop")
                    clear_all_caches_btn = gr.Button("🧹 清理全部缓存", variant="stop")

                cache_status = gr.Textbox(label="状态", interactive=False)

            # Tab 2: 摘要缓存
            with gr.Tab("📋 摘要缓存"):
                gr.Markdown("#### 章节摘要缓存")

                summaries_table = gr.Dataframe(
                    headers=["项目ID", "摘要数量", "缓存时间", "大小"],
                    interactive=False
                )

                with gr.Row():
                    refresh_summaries_btn = gr.Button("🔄 刷新列表", size="sm")
                    summary_size_info = gr.Textbox(label="缓存大小", interactive=False, lines=1)
                    clear_summaries_btn = gr.Button("🧹 清理全部摘要", variant="stop")

                summary_status = gr.Textbox(label="状态", interactive=False)

        # 事件处理
        def on_refresh_caches():
            try:
                caches = list_generation_caches()
                import pandas as pd

                if not caches:
                    return (
                        pd.DataFrame(columns=["项目ID", "项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
                        "✅ 暂无生成缓存",
                        get_generation_cache_size()
                    )

                df = pd.DataFrame([
                    {
                        "项目ID": c["project_id"],
                        "项目名": c["title"],
                        "当前章节": c["current_chapter"],
                        "总章节": c["total_chapters"],
                        "状态": c["status"],
                        "缓存时间": c["timestamp"][:19] if c["timestamp"] else "",
                        "大小(KB)": round(c["size"] / 1024, 2)
                    }
                    for c in caches
                ])
                return df, f"✅ 找到 {len(caches)} 个缓存", get_generation_cache_size()

            except Exception as e:
                logger.error(f"刷新缓存列表失败: {e}")
                import pandas as pd
                return (
                    pd.DataFrame(columns=["项目ID", "项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
                    f"❌ 刷新失败: {str(e)}",
                    get_generation_cache_size()
                )

        def on_clear_selected_cache(table_data):
            import pandas as pd

            # 检查table_data是否为空或无效
            if table_data is None:
                return (
                    "❌ 请先刷新缓存列表",
                    pd.DataFrame(columns=["项目ID", "项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
                    get_generation_cache_size()
                )

            # 处理pandas DataFrame
            if hasattr(table_data, 'empty'):
                if table_data.empty:
                    return (
                        "❌ 请先选择要清理的缓存",
                        pd.DataFrame(columns=["项目ID", "项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
                        get_generation_cache_size()
                    )
                # 获取第一行第一列
                table_list = table_data.values.tolist()
            else:
                table_list = table_data

            if not table_list or len(table_list) == 0:
                return (
                    "❌ 缓存列表为空",
                    pd.DataFrame(columns=["项目ID", "项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
                    get_generation_cache_size()
                )

            # 获取项目ID（第一行第一列）
            project_id = table_list[0][0]
            if not project_id or project_id == "暂无生成缓存":
                return (
                    "❌ 无效的项目ID",
                    pd.DataFrame(columns=["项目ID", "项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
                    get_generation_cache_size()
                )

            success, msg = clear_generation_cache(project_id)
            if success:
                # 刷新列表
                return on_refresh_caches()
            else:
                return (
                    f"✗ {msg}",
                    pd.DataFrame(columns=["项目ID", "项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
                    get_generation_cache_size()
                )

        def on_clear_all_caches():
            import pandas as pd
            success, msg = clear_all_generation_caches()
            if success:
                return on_refresh_caches()
            else:
                return (
                    f"✗ {msg}",
                    pd.DataFrame(columns=["项目ID", "项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
                    get_generation_cache_size()
                )

        def on_refresh_summaries():
            try:
                caches = list_summary_caches()
                import pandas as pd

                if not caches:
                    return (
                        pd.DataFrame(columns=["项目ID", "摘要数量", "缓存时间", "大小"]),
                        "✅ 暂无摘要缓存",
                        get_summary_cache_size()
                    )

                df = pd.DataFrame([
                    {
                        "项目ID": c["project_id"],
                        "摘要数量": c["count"],
                        "缓存时间": c["timestamp"][:19] if c["timestamp"] else "",
                        "大小": round(c["size"] / 1024, 2)
                    }
                    for c in caches
                ])
                return df, f"✅ 找到 {len(caches)} 个项目", get_summary_cache_size()

            except Exception as e:
                logger.error(f"刷新摘要缓存失败: {e}")
                import pandas as pd
                return (
                    pd.DataFrame(columns=["项目ID", "摘要数量", "缓存时间", "大小"]),
                    f"❌ 刷新失败: {str(e)}",
                    get_summary_cache_size()
                )

        def on_clear_all_summaries():
            import pandas as pd
            success, msg = clear_all_summary_caches()
            if success:
                return on_refresh_summaries()
            else:
                return (
                    f"✗ {msg}",
                    pd.DataFrame(columns=["项目ID", "摘要数量", "缓存时间", "大小"]),
                    get_summary_cache_size()
                )

        # 绑定事件 - 生成缓存
        refresh_caches_btn.click(
            fn=on_refresh_caches,
            outputs=[caches_table, cache_status, cache_size_info]
        )

        clear_cache_btn.click(
            fn=on_clear_selected_cache,
            inputs=[caches_table],
            outputs=[cache_status, caches_table, cache_size_info]
        )

        clear_all_caches_btn.click(
            fn=on_clear_all_caches,
            outputs=[cache_status, caches_table, cache_size_info]
        )

        # 绑定事件 - 摘要缓存
        refresh_summaries_btn.click(
            fn=on_refresh_summaries,
            outputs=[summaries_table, summary_status, summary_size_info]
        )

        clear_summaries_btn.click(
            fn=on_clear_all_summaries,
            outputs=[summary_status, summaries_table, summary_size_info]
        )

    return cache_ui
