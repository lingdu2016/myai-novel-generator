"""
Supabase 客户端模块 - 为 Hugging Face Spaces 提供云端数据持久化

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import json
import logging
import os
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)

# 全局 Supabase 客户端实例
_supabase_client: Optional[Any] = None
_sync_enabled: bool = False


def get_supabase_client() -> Optional[Any]:
    """
    获取 Supabase 客户端实例

    Returns:
        Supabase 客户端实例，如果未配置则返回 None
    """
    global _supabase_client, _sync_enabled

    if _supabase_client is not None:
        return _supabase_client

    # 检查环境变量
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.debug("Supabase 环境变量未设置，跳过云端同步")
        return None

    try:
        from supabase import create_client

        _supabase_client = create_client(supabase_url, supabase_key)
        _sync_enabled = True

        logger.info(f"Supabase 客户端初始化成功: {supabase_url}")
        return _supabase_client

    except ImportError:
        logger.warning("supabase 包未安装，云端同步功能不可用")
        return None
    except Exception as e:
        logger.error(f"Supabase 客户端初始化失败: {e}")
        return None


def is_sync_enabled() -> bool:
    """检查云端同步是否启用"""
    global _sync_enabled
    return _sync_enabled and _supabase_client is not None


def get_user_id() -> str:
    """
    获取用户ID（用于多用户隔离）

    Returns:
        用户ID，默认为 "default"
    """
    # 在 HF Spaces 中，可以使用环境变量区分用户
    # 或者使用一个固定的标识符
    return os.environ.get("HF_USER", "default")


class ProjectSyncManager:
    """项目数据同步管理器"""

    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = "projects"

    def sync_project(self, project_id: str, project_data: Dict) -> bool:
        """
        同步项目数据到 Supabase

        Args:
            project_id: 项目ID
            project_data: 项目数据

        Returns:
            是否同步成功
        """
        if not is_sync_enabled() or not self.client:
            return False

        try:
            # 准备数据
            data = {
                "id": project_id,
                "user_id": get_user_id(),
                "title": project_data.get("title", ""),
                "genre": project_data.get("genre", ""),
                "character_setting": project_data.get("character_setting", ""),
                "world_setting": project_data.get("world_setting", ""),
                "plot_idea": project_data.get("plot_idea", ""),
                "chapter_count": project_data.get("chapter_count", 0),
                "outline": json.dumps(project_data.get("outline", [])),
                "chapters": json.dumps(project_data.get("chapters", [])),
                "coherence_data": json.dumps(project_data.get("coherence_data", {})),
                "updated_at": datetime.now().isoformat(),
            }

            # 检查项目是否已存在
            result = self.client.table(self.table_name).select("id").eq("id", project_id).execute()

            if result.data:
                # 更新现有项目
                result = (
                    self.client.table(self.table_name).update(data).eq("id", project_id).execute()
                )
                logger.info(f"项目已更新到云端: {project_id}")
            else:
                # 插入新项目
                data["created_at"] = project_data.get("created_at", datetime.now().isoformat())
                result = self.client.table(self.table_name).insert(data).execute()
                logger.info(f"项目已同步到云端: {project_id}")

            return True

        except Exception as e:
            logger.error(f"同步项目到云端失败: {e}")
            return False

    def get_project(self, project_id: str) -> Optional[Dict]:
        """
        从 Supabase 获取项目数据

        Args:
            project_id: 项目ID

        Returns:
            项目数据字典，如果不存在则返回 None
        """
        if not is_sync_enabled() or not self.client:
            return None

        try:
            result = self.client.table(self.table_name).select("*").eq("id", project_id).execute()

            if result.data:
                row = result.data[0]
                # 解析 JSON 字段
                return {
                    "id": row["id"],
                    "title": row["title"],
                    "genre": row["genre"],
                    "character_setting": row["character_setting"],
                    "world_setting": row["world_setting"],
                    "plot_idea": row["plot_idea"],
                    "chapter_count": row["chapter_count"],
                    "outline": json.loads(row["outline"]) if row["outline"] else [],
                    "chapters": json.loads(row["chapters"]) if row["chapters"] else [],
                    "coherence_data": json.loads(row["coherence_data"])
                    if row["coherence_data"]
                    else {},
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }

            return None

        except Exception as e:
            logger.error(f"从云端获取项目失败: {e}")
            return None

    def list_projects(self) -> List[Dict]:
        """
        从 Supabase 获取项目列表

        Returns:
            项目列表
        """
        if not is_sync_enabled() or not self.client:
            return []

        try:
            user_id = get_user_id()
            result = (
                self.client.table(self.table_name)
                .select("id, title, genre, created_at, updated_at, chapter_count")
                .eq("user_id", user_id)
                .execute()
            )

            projects = []
            for row in result.data:
                projects.append(
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "genre": row["genre"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "chapter_count": row["chapter_count"],
                    }
                )

            return projects

        except Exception as e:
            logger.error(f"从云端获取项目列表失败: {e}")
            return []

    def delete_project(self, project_id: str) -> bool:
        """
        从 Supabase 删除项目

        Args:
            project_id: 项目ID

        Returns:
            是否删除成功
        """
        if not is_sync_enabled() or not self.client:
            return False

        try:
            self.client.table(self.table_name).delete().eq("id", project_id).execute()

            logger.info(f"项目已从云端删除: {project_id}")
            return True

        except Exception as e:
            logger.error(f"从云端删除项目失败: {e}")
            return False


class ConfigSyncManager:
    """用户配置同步管理器"""

    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = "configs"

    def sync_config(self, config_data: Dict) -> bool:
        """
        同步用户配置到 Supabase

        Args:
            config_data: 配置数据

        Returns:
            是否同步成功
        """
        if not is_sync_enabled() or not self.client:
            return False

        try:
            user_id = get_user_id()

            data = {
                "user_id": user_id,
                "providers": json.dumps(config_data.get("providers", {})),
                "generation_params": json.dumps(config_data.get("generation_params", {})),
                "updated_at": datetime.now().isoformat(),
            }

            # 检查配置是否已存在
            result = (
                self.client.table(self.table_name)
                .select("user_id")
                .eq("user_id", user_id)
                .execute()
            )

            if result.data:
                result = (
                    self.client.table(self.table_name).update(data).eq("user_id", user_id).execute()
                )
            else:
                result = self.client.table(self.table_name).insert(data).execute()

            logger.info("用户配置已同步到云端")
            return True

        except Exception as e:
            logger.error(f"同步配置到云端失败: {e}")
            return False

    def get_config(self) -> Optional[Dict]:
        """
        从 Supabase 获取用户配置

        Returns:
            配置数据字典，如果不存在则返回 None
        """
        if not is_sync_enabled() or not self.client:
            return None

        try:
            user_id = get_user_id()
            result = self.client.table(self.table_name).select("*").eq("user_id", user_id).execute()

            if result.data:
                row = result.data[0]
                return {
                    "providers": json.loads(row["providers"]) if row["providers"] else {},
                    "generation_params": json.loads(row["generation_params"])
                    if row["generation_params"]
                    else {},
                    "updated_at": row["updated_at"],
                }

            return None

        except Exception as e:
            logger.error(f"从云端获取配置失败: {e}")
            return None


class CacheSyncManager:
    """生成进度缓存同步管理器"""

    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = "generation_cache"

    def sync_cache(self, project_id: str, cache_data: Dict) -> bool:
        """
        同步生成缓存到 Supabase

        Args:
            project_id: 项目ID
            cache_data: 缓存数据

        Returns:
            是否同步成功
        """
        if not is_sync_enabled() or not self.client:
            return False

        try:
            data = {
                "project_id": project_id,
                "current_chapter": cache_data.get("current_chapter", 0),
                "outline_progress": json.dumps(cache_data.get("outline_progress", {})),
                "coherence_snapshot": json.dumps(cache_data.get("coherence_snapshot", {})),
                "updated_at": datetime.now().isoformat(),
            }

            # 检查缓存是否已存在
            result = (
                self.client.table(self.table_name)
                .select("project_id")
                .eq("project_id", project_id)
                .execute()
            )

            if result.data:
                result = (
                    self.client.table(self.table_name)
                    .update(data)
                    .eq("project_id", project_id)
                    .execute()
                )
            else:
                result = self.client.table(self.table_name).insert(data).execute()

            logger.debug(f"生成缓存已同步到云端: {project_id}")
            return True

        except Exception as e:
            logger.error(f"同步缓存到云端失败: {e}")
            return False

    def get_cache(self, project_id: str) -> Optional[Dict]:
        """
        从 Supabase 获取生成缓存

        Args:
            project_id: 项目ID

        Returns:
            缓存数据字典，如果不存在则返回 None
        """
        if not is_sync_enabled() or not self.client:
            return None

        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .eq("project_id", project_id)
                .execute()
            )

            if result.data:
                row = result.data[0]
                return {
                    "current_chapter": row["current_chapter"],
                    "outline_progress": json.loads(row["outline_progress"])
                    if row["outline_progress"]
                    else {},
                    "coherence_snapshot": json.loads(row["coherence_snapshot"])
                    if row["coherence_snapshot"]
                    else {},
                    "updated_at": row["updated_at"],
                }

            return None

        except Exception as e:
            logger.error(f"从云端获取缓存失败: {e}")
            return None

    def delete_cache(self, project_id: str) -> bool:
        """
        从 Supabase 删除生成缓存

        Args:
            project_id: 项目ID

        Returns:
            是否删除成功
        """
        if not is_sync_enabled() or not self.client:
            return False

        try:
            self.client.table(self.table_name).delete().eq("project_id", project_id).execute()

            logger.debug(f"生成缓存已从云端删除: {project_id}")
            return True

        except Exception as e:
            logger.error(f"从云端删除缓存失败: {e}")
            return False


def restore_projects_from_cloud(projects_dir: Path) -> int:
    """
    启动时从云端恢复项目到本地

    Args:
        projects_dir: 本地项目目录

    Returns:
        恢复的项目数量
    """
    if not is_sync_enabled():
        logger.info("云端同步未启用，跳过从云端恢复")
        return 0

    try:
        sync_manager = ProjectSyncManager()
        cloud_projects = sync_manager.list_projects()

        if not cloud_projects:
            logger.info("云端没有项目数据")
            return 0

        restored_count = 0

        for cloud_project in cloud_projects:
            project_id = cloud_project["id"]
            local_file = projects_dir / f"{project_id}.json"

            # 获取云端完整数据
            cloud_data = sync_manager.get_project(project_id)
            if not cloud_data:
                continue

            # 检查本地是否已存在
            if local_file.exists():
                try:
                    with open(local_file, encoding="utf-8") as f:
                        local_data = json.load(f)

                    local_updated = local_data.get("updated_at", "")
                    cloud_updated = cloud_data.get("updated_at", "")

                    # 如果云端数据更新，则覆盖本地
                    if cloud_updated > local_updated:
                        with open(local_file, "w", encoding="utf-8") as f:
                            json.dump(cloud_data, f, ensure_ascii=False, indent=2)
                        logger.info(f"项目已从云端更新: {project_id}")
                        restored_count += 1
                    else:
                        logger.debug(f"本地数据已是最新，跳过: {project_id}")

                except Exception as e:
                    logger.warning(f"检查本地项目失败，使用云端数据: {e}")
                    with open(local_file, "w", encoding="utf-8") as f:
                        json.dump(cloud_data, f, ensure_ascii=False, indent=2)
                    restored_count += 1
            else:
                # 本地不存在，直接保存云端数据
                with open(local_file, "w", encoding="utf-8") as f:
                    json.dump(cloud_data, f, ensure_ascii=False, indent=2)
                logger.info(f"项目已从云端恢复: {project_id}")
                restored_count += 1

        logger.info(f"从云端恢复了 {restored_count} 个项目")
        return restored_count

    except Exception as e:
        logger.error(f"从云端恢复项目失败: {e}")
        return 0


def restore_config_from_cloud(config_file: Path) -> bool:
    """
    启动时从云端恢复配置到本地

    Args:
        config_file: 本地配置文件路径

    Returns:
        是否成功恢复
    """
    if not is_sync_enabled():
        return False

    try:
        sync_manager = ConfigSyncManager()
        cloud_config = sync_manager.get_config()

        if not cloud_config:
            logger.info("云端没有配置数据")
            return False

        # 合并云端配置到本地
        local_config = {}
        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    local_config = json.load(f)
            except Exception as e:
                logger.warning(f"读取本地配置失败: {e}")

        # 优先使用云端配置
        cloud_providers = cloud_config.get("providers", {})
        if cloud_providers:
            local_config["providers"] = cloud_providers
            logger.info("API 提供商配置已从云端恢复")

        cloud_gen_params = cloud_config.get("generation_params", {})
        if cloud_gen_params:
            local_config["generation_params"] = cloud_gen_params
            logger.info("生成参数已从云端恢复")

        # 保存合并后的配置
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(local_config, f, ensure_ascii=False, indent=2)

        logger.info("配置已从云端恢复")
        return True

    except Exception as e:
        logger.error(f"从云端恢复配置失败: {e}")
        return False


def get_sync_status() -> Dict[str, Any]:
    """
    获取同步状态信息

    Returns:
        同步状态字典
    """
    client = get_supabase_client()

    status = {
        "enabled": is_sync_enabled(),
        "url": os.environ.get("SUPABASE_URL", ""),
        "has_key": bool(os.environ.get("SUPABASE_KEY")),
        "user_id": get_user_id(),
    }

    if client and is_sync_enabled():
        try:
            # 尝试获取项目数量
            project_sync = ProjectSyncManager()
            projects = project_sync.list_projects()
            status["cloud_projects_count"] = len(projects)
            status["connected"] = True
        except Exception as e:
            status["connected"] = False
            status["error"] = str(e)
    else:
        status["connected"] = False

    return status
