# AI Novel Generator 4.5 - API参考文档

**版本**: 4.5.0  
**更新**: 2026-03-08

---

## 目录

1. [模块导入](#模块导入)
2. [连贯性系统API](#连贯性系统api)
3. [提示词系统API](#提示词系统api)
4. [API客户端API](#api客户端api)
5. [配置管理API](#配置管理api)
6. [示例代码](#示例代码)

---

## 模块导入

### 基础导入

```python
from src import (
    UnifiedAPIClient,
    CharacterTracker,
    PlotManager,
    WorldDatabase,
    PromptManager
)
```

### 延迟导入

```python
# 按需导入，避免循环依赖
from src.core.coherence import CharacterTracker
from src.core.prompts import PromptManager
from src.config.providers import ProviderFactory
```

---

## 连贯性系统API

### CharacterTracker

#### 初始化

```python
from src.core.coherence import CharacterTracker

tracker = CharacterTracker(
    project_id="my_novel",
    cache_dir=Path("cache/coherence")  # 可选
)
```

#### 方法

**track_character_appearance()**
```python
tracker.track_character_appearance(
    chapter_num=1,
    character_name="张三",
    context="主角首次出现",
    personality_hint="勇敢坚毅"  # 可选
)
```

**update_character_state()**
```python
tracker.update_character_state(
    chapter_num=2,
    character_name="张三",
    updates={
        "mood": "兴奋",
        "location": "青云宗",
        "goals": ["修炼升级", "寻找宝藏"]
    }
)
```

**get_character_current_state()**
```python
state = tracker.get_character_current_state("张三")
print(state.personality, state.mood, state.location)
```

**get_character_summary_for_context()**
```python
summary = tracker.get_character_summary_for_context(
    character_name="张三",
    up_to_chapter=5
)
```

---

### PlotManager

#### 初始化

```python
from src.core.coherence import PlotManager

manager = PlotManager(
    project_id="my_novel",
    cache_dir=Path("cache/coherence")
)
```

#### 方法

**add_plot_thread()**
```python
manager.add_plot_thread(
    thread_id="main_1",
    name="主线剧情",
    plot_type="main",  # main/side/character/romance/mystery/conflict
    description="张三修仙成长",
    chapter_num=1,
    related_characters=["张三", "李四"]  # 可选
)
```

**add_plot_event()**
```python
manager.add_plot_event(
    thread_id="main_1",
    chapter_num=2,
    description="张三突破筑基期"
)
```

**add_foreshadowing()**
```python
manager.add_foreshadowing(
    thread_id="main_1",
    foreshadowing="神秘玉佩的秘密身份"
)
```

**resolve_foreshadowing()**
```python
manager.resolve_foreshadowing(
    foreshadowing="神秘玉佩的秘密身份",
    resolution_chapter=10,
    resolution_description="玉佩是上古大能的传承"
)
```

---

### WorldDatabase

#### 初始化

```python
from src.core.coherence import WorldDatabase

db = WorldDatabase(
    project_id="my_novel",
    cache_dir=Path("cache/coherence")
)
```

#### 方法

**add_location()**
```python
db.add_location(
    name="青云宗",
    location_type="宗门",  # city/forest/building/etc
    description="修仙门派",
    features=["灵气充沛", "历史悠久"],
    chapter_num=1
)
```

**add_item()**
```python
db.add_item(
    name="飞剑",
    item_type="武器",
    description="修仙者的武器",
    powers=["飞行", "斩妖"],
    owner="张三",
    chapter_num=1
)
```

**add_rule()**
```python
db.add_rule(
    name="修仙体系",
    category="修炼",
    description="境界划分",
    constraints=["需要灵气", "有心魔风险"],
    examples=["练气期", "筑基期"]
)
```

---

### ContextBuilder

#### 使用智能上下文生成

```python
from src.core.coherence import build_context_for_generation

context = build_context_for_generation(
    current_chapter=5,
    chapter_outline="主角进入秘境",
    chapter_desc="探索神秘遗迹",
    character_tracker=tracker,
    plot_manager=manager,
    world_db=world_db,
    api_client=api_client,
    max_length=2000
)
```

---

### CoherenceValidator

#### 验证章节连贯性

```python
from src.core.coherence import validate_chapter_coherence

result = validate_chapter_coherence(
    chapter_content="章节内容...",
    chapter_num=5,
    chapter_outline="章节大纲",
    character_tracker=tracker,
    plot_manager=manager,
    world_db=world_db,
    api_client=api_client
)

print(f"评分: {result.score}")
print(f"问题数: {len(result.issues)}")
```

---

## 提示词系统API

### PromptManager

#### 初始化

```python
from src.core.prompts import PromptManager

manager = PromptManager(
    config_dir=Path("config")
)
```

#### 方法

**get_template()**
```python
template = manager.get_template(
    category="generation",
    name="默认",
    use_preset=True
)
```

**set_template()**
```python
manager.set_template(
    category="generation",
    name="自定义模板",
    template="请生成：{title} - {chapter_desc}"
)
```

**apply_variables()**
```python
result = manager.apply_variables(
    template="{title} - 第{chapter_num}章",
    variables={
        "title": "我的小说",
        "chapter_num": 1
    }
)
```

**export_templates()**
```python
json_str = manager.export_templates(
    categories=["generation", "rewrite"]
)
```

**import_templates()**
```python
count = manager.import_templates(
    json_str=json_data,
    overwrite=False
)
```

---

### PromptVariableManager

#### 初始化

```python
from src.core.prompts.variables import PromptVariableManager

vm = PromptVariableManager()
```

#### 方法

**apply_variables()**
```python
result = vm.apply_variables(
    template="{title} - {chapter_num}章: {chapter_title}",
    variables={
        "title": "测试",
        "chapter_num": 1,
        "chapter_title": "开始"
    }
)
```

**get_variables_info()**
```python
variables = vm.get_variables_info()
for var in variables:
    print(f"{var['name']}: {var['description']}")
```

---

## API客户端API

### UnifiedAPIClient

#### 初始化

```python
from src.api import create_api_client

client = create_api_client([
    {
        "provider_id": "openai",
        "api_key": "sk-...",
        "enabled": True
    },
    {
        "provider_id": "deepseek",
        "api_key": "sk-...",
        "enabled": True
    }
])
```

#### 方法

**generate()**
```python
content = client.generate(
    messages=[
        {"role": "system", "content": "你是一个小说作家"},
        {"role": "user", "content": "写一首诗"}
    ],
    model="gpt-4o",  # 可选
    temperature=0.8,  # 可选
    max_tokens=1000,  # 可选
    use_cache=True,  # 可选
    max_retries=3  # 可选
)
```

**test_connection()**
```python
results = client.test_connection()
for provider, is_connected in results.items():
    print(f"{provider}: {'✓' if is_connected else '✗'}")
```

---

### ResponseCache

#### 初始化

```python
from src.api import ResponseCache

cache = ResponseCache(
    max_size=1000,
    cache_dir=Path("cache/api")
)
```

#### 方法

**get()**
```python
cached = cache.get(
    messages=[...],
    model="gpt-4o"
)
```

**set()**
```python
cache.set(
    messages=[...],
    model="gpt-4o",
    value="生成的文本",
    ttl=3600  # 缓存1小时
)
```

**clear()**
```python
cache.clear()
```

---

## 配置管理API

### ProviderFactory

#### 方法

**get_provider_config()**
```python
from src.config.providers import ProviderFactory

config = ProviderFactory.get_provider_config("openai")
print(config.name, config.base_url, config.models)
```

**list_providers()**
```python
providers = ProviderFactory.list_providers()
print(providers)  # ['openai', 'anthropic', 'google', ...]
```

**list_providers_with_info()**
```python
providers = ProviderFactory.list_providers_with_info()
for p in providers:
    print(f"{p['name']}: {p['description']}")
```

**add_custom_provider()**
```python
ProviderFactory.add_custom_provider(
    provider_id="my_provider",
    name="我的提供商",
    base_url="https://api.example.com/v1",
    models=["model-1", "model-2"],
    default_model="model-1",
    requires_key=True
)
```

---

## 示例代码

### 示例1：创建项目并生成章节

```python
from src.ui.app import create_new_project, generate_chapter

# 创建项目
status, project_id = create_new_project(
    title="修仙之旅",
    genre="玄幻仙侠",
    character_setting="主角张三...",
    world_setting="修仙世界...",
    plot_idea="张三修仙成长...",
    chapter_count=50
)

# 生成第一章
content, status, validation = generate_chapter(
    chapter_num=1,
    chapter_title="初入仙门",
    chapter_desc="张三在山中采药时...",
    target_words=3000,
    use_coherence=True
)
```

### 示例2：使用连贯性系统

```python
from src.core.coherence import (
    CharacterTracker,
    PlotManager,
    WorldDatabase,
    build_context_for_generation,
    validate_chapter_coherence
)

# 初始化系统
char_tracker = CharacterTracker("my_novel")
plot_manager = PlotManager("my_novel")
world_db = WorldDatabase("my_novel")

# 跟踪角色
char_tracker.track_character_appearance(1, "张三", "首次出现", "勇敢")
char_tracker.update_character_state(1, "张三", {"mood": "兴奋"})

# 添加剧情线
plot_manager.add_plot_thread("main_1", "主线", "main", "修仙成长", 1)
plot_manager.add_foreshadowing("main_1", "神秘玉佩的秘密")

# 生成智能上下文
context = build_context_for_generation(
    current_chapter=2,
    chapter_outline="继续冒险",
    chapter_desc="张三在青云宗的学习生活",
    character_tracker=char_tracker,
    plot_manager=plot_manager,
    world_db=world_db,
    api_client=api_client
)

# 验证连贯性
result = validate_chapter_coherence(
    chapter_content=generated_text,
    chapter_num=2,
    chapter_outline="继续冒险",
    character_tracker=char_tracker,
    plot_manager=plot_manager,
    world_db=world_db,
    api_client=api_client
)
```

### 示例3：自定义提示词

```python
from src.core.prompts import PromptManager

manager = PromptManager()

# 创建自定义模板
manager.set_template(
    category="generation",
    name="我的风格",
    template="""请根据以下信息创作小说章节：

【小说】{title}
【章节】第{chapter_num}章 - {chapter_title}

【大纲】
{chapter_desc}

【前文回顾】
{context}

【写作要求】
- 字数：约{target_words}字
- 风格：{style}
- 保持与前文连贯

请开始创作："""
)

# 使用自定义模板
template = manager.get_template("generation", "我的风格")
prompt = manager.apply_variables(template, {...})
```

### 示例4：多提供商配置

```python
from src.api import create_api_client

client = create_api_client([
    {
        "provider_id": "openai",
        "api_key": "sk-...",
        "enabled": True,
        "model": "gpt-4o"
    },
    {
        "provider_id": "deepseek",
        "api_key": "sk-...",
        "enabled": True,
        "model": "deepseek-chat"
    },
    {
        "provider_id": "ollama",
        "enabled": True  # 本地免费
    }
])

# 自动负载均衡
content1 = client.generate(messages=[...], model="gpt-4o")
content2 = client.generate(messages=[...])  # 自动使用deepseek
content3 = client.generate(messages=[...])  # 自动使用ollama
```

---

## 错误处理

### 常见异常

```python
# API调用异常
from openai import RateLimitError, APIError

try:
    content = client.generate(messages=[...])
except RateLimitError:
    print("速率限制，请稍后重试")
except APIError as e:
    print(f"API错误: {e}")
```

### 连贯性系统异常

```python
# 验证失败
result = validate_chapter_coherence(...)

if not result.is_valid:
    print(f"验证失败: {result.summary}")
    for issue in result.issues:
        if issue.severity == "error":
            print(f"错误: {issue.description}")
```

---

**版权所有 © 2026 新疆幻城网安科技有限责任公司**
