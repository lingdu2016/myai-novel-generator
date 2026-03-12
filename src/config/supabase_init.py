"""
Supabase 数据库表初始化 SQL 脚本

在 Supabase Dashboard 的 SQL Editor 中执行以下脚本创建所需表

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

# SQL 脚本用于在 Supabase 中创建所需的数据库表

PROJECTS_TABLE_SQL = """
-- 创建 projects 表 - 存储项目元数据
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    title TEXT,
    genre TEXT,
    character_setting TEXT,
    world_setting TEXT,
    plot_idea TEXT,
    chapter_count INTEGER DEFAULT 0,
    outline JSONB DEFAULT '[]'::jsonb,
    chapters JSONB DEFAULT '[]'::jsonb,
    coherence_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE projects IS '存储小说项目数据';
"""

CONFIGS_TABLE_SQL = """
-- 创建 configs 表 - 存储用户配置
CREATE TABLE IF NOT EXISTS configs (
    user_id TEXT PRIMARY KEY,
    providers JSONB DEFAULT '{}'::jsonb,
    generation_params JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建更新时间触发器
DROP TRIGGER IF EXISTS update_configs_updated_at ON configs;
CREATE TRIGGER update_configs_updated_at
    BEFORE UPDATE ON configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE configs IS '存储用户API配置和生成参数';
"""

CACHE_TABLE_SQL = """
-- 创建 generation_cache 表 - 存储生成进度缓存
CREATE TABLE IF NOT EXISTS generation_cache (
    project_id TEXT PRIMARY KEY,
    current_chapter INTEGER DEFAULT 0,
    outline_progress JSONB DEFAULT '{}'::jsonb,
    coherence_snapshot JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建更新时间触发器
DROP TRIGGER IF EXISTS update_cache_updated_at ON generation_cache;
CREATE TRIGGER update_cache_updated_at
    BEFORE UPDATE ON generation_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE generation_cache IS '存储小说生成进度缓存';
"""

# RLS (Row Level Security) 配置
RLS_CONFIG_SQL = """
-- 启用行级安全策略
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_cache ENABLE ROW LEVEL SECURITY;

-- 创建策略：用户只能访问自己的数据
CREATE POLICY IF NOT EXISTS "Users can only access their own projects"
    ON projects FOR ALL
    USING (user_id = current_setting('app.current_user_id', true)::text);

CREATE POLICY IF NOT EXISTS "Users can only access their own configs"
    ON configs FOR ALL
    USING (user_id = current_setting('app.current_user_id', true)::text);

-- 注意：generation_cache 使用 project_id 关联到 projects 表
-- 如果需要更严格的权限控制，可以在应用层实现
"""


def get_all_sql() -> str:
    """
    获取所有 SQL 脚本

    Returns:
        完整的 SQL 脚本字符串
    """
    return f"""
-- ============================================
-- AI Novel Generator 4.5 - Supabase 数据库初始化
-- 版权所有 © 2026 新疆幻城网安科技有限责任公司
-- ============================================

{PROJECTS_TABLE_SQL}

{CONFIGS_TABLE_SQL}

{CACHE_TABLE_SQL}

-- RLS 安全配置（可选，根据安全需求启用）
-- {RLS_CONFIG_SQL}

-- ============================================
-- 初始化完成
-- ============================================
"""


def print_setup_instructions():
    """打印设置说明"""
    print("""
============================================
Supabase 数据库设置说明
============================================

1. 注册并创建 Supabase 项目:
   - 访问 https://supabase.com
   - 使用 GitHub 账号登录
   - 创建新项目（免费版支持 500MB 数据库 + 1GB 存储）

2. 在 SQL Editor 中创建表:
   - 进入 Supabase Dashboard
   - 点击左侧 "SQL Editor"
   - 新建查询
   - 复制下面的 SQL 脚本并执行

3. 获取连接信息:
   - 点击左侧 "Settings" > "API"
   - 复制 "Project URL" 和 "anon public" API Key

4. 在 Hugging Face Spaces 中设置环境变量:
   - 进入你的 Space 设置
   - 添加 Secrets:
     * SUPABASE_URL = your_project_url
     * SUPABASE_KEY = your_anon_key

============================================
SQL 创建脚本
============================================
""")
    print(get_all_sql())
    print("""
============================================
配置完成！
============================================
现在你的 HF Space 重启后可以从云端自动恢复数据。

注意事项:
1. 免费版 Supabase 有 500MB 数据库限制，大型项目可能受限
2. 建议使用 API Key 而不是 Service Role Key，更安全
3. 如果不需要云端同步，不设置环境变量即可，程序会降级到本地存储
4. 网络断开时仍可正常使用，只是同步会延迟
""")


if __name__ == "__main__":
    print_setup_instructions()
