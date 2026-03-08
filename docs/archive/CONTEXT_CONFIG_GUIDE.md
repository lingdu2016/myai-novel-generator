# 上下文配置系统 - 统一架构说明

## 概述

上下文配置系统已**完全统一**到「系统设置 > 生成参数配置」中，删除了所有重复的配置项。

## 配置位置

**唯一配置入口**：`系统设置` → `生成参数配置` → `上下文管理` 区域

### 配置项说明

| 配置项 | 类型 | 范围/选项 | 默认值 | 说明 |
|--------|------|-----------|--------|------|
| **启用上下文机制** | Checkbox | ✓/✗ | ✅ | 总开关，关闭后完全不使用上下文 |
| **上下文模式** | Radio | summary/full/disabled | summary | 摘要/全文/关闭三种模式 |
| **最大章节数** | Slider | 1-100 | 50 | 最多使用前面多少章作为上下文 |
| **自动分配token** | Checkbox | ✓/✗ | ✅ | 智能分配可用token给不同上下文元素 |

### 上下文模式详解

#### 1. Summary（摘要模式）- 默认推荐
- **使用内容**：章节摘要 + 最近10章标题
- **摘要生成**：✅ 每章生成后自动创建摘要
- **Token消耗**：低（节省90%+ token）
- **连贯性**：中等
- **适用场景**：
  - 长篇小说（50+章）
  - Token预算有限
  - 注重成本效益

**示例**：
```
第100章生成时：
- 使用第51-99章的摘要（49个摘要）
- 使用第91-99章的完整标题（9个标题）
- 总token消耗：约2000-5000 tokens
```

#### 2. Full（全文模式）- 高质量
- **使用内容**：完整章节内容 + 最近5章摘要
- **摘要生成**：❌ 不生成摘要
- **Token消耗**：高
- **连贯性**：最高
- **适用场景**：
  - 短篇小说（<20章）
  - 追求最高连贯性
  - Token预算充足

**示例**：
```
第10章生成时（max_chapters=50）：
- 使用第1-9章的完整内容
- 使用第6-9章的摘要作为辅助
- 总token消耗：约50,000-150,000 tokens
```

#### 3. Disabled（关闭模式）- 最快速度
- **使用内容**：无
- **摘要生成**：❌ 不生成摘要
- **Token消耗**：最低
- **连贯性**：最低
- **适用场景**：
  - 测试生成效果
  - 快速原型
  - 不需要连贯性

## 智能章节计算

系统根据当前章节号和`max_chapters`配置，自动计算使用哪些章节：

```python
if chapter_num > max_chapters:
    start_idx = chapter_num - max_chapters - 1
    used_chapters = previous_chapters[start_idx:]
else:
    used_chapters = previous_chapters  # 使用所有前面章节
```

### 实际计算示例

假设 `max_chapters = 50`：

| 当前章节 | 使用的章节 | 说明 |
|----------|------------|------|
| 第5章 | 第1-4章 | 章节不足，使用全部 |
| 第10章 | 第1-9章 | 章节不足，使用全部 |
| 第50章 | 第1-49章 | 章节不足，使用全部 |
| **第55章** | **第6-54章** | **达到上限，使用前50章** |
| 第100章 | 第51-99章 | 达到上限，使用最新50章 |

## 配置文件

所有配置保存在：`config/generation_config.json`

### 配置文件结构

```json
{
  "temperature": 0.85,
  "top_p": 0.92,
  "top_k": 50,
  "max_tokens": 20000,
  "target_words": 3000,
  "writing_style": "详细生动",
  "writing_tone": "第三人称",
  "character_dev": "平衡发展",
  "plot_complexity": "中等复杂",

  // 上下文管理配置
  "context_enable": true,
  "context_mode": "summary",
  "context_max_chapters": 50,
  "context_auto_allocate": true
}
```

## 代码实现

### 智能上下文构建器

位置：`src/ui/features/auto_generation.py`

```python
def _build_smart_context(
    self,
    project_id: str,
    chapter_num: int,
    previous_chapters: List[Dict],
    max_tokens: int
) -> Tuple[str, bool]:
    """
    智能构建上下文

    返回: (context_text, should_generate_summary)
    """
    # 1. 读取配置
    context_config = load_context_config()

    # 2. 检查是否启用
    if not context_config["context_enable"]:
        return "【这是第一章，直接开始创作】", True

    # 3. 计算使用的章节
    max_chapters = context_config["context_max_chapters"]
    if chapter_num > max_chapters:
        start_idx = chapter_num - max_chapters - 1
        relevant_chapters = previous_chapters[start_idx:]
    else:
        relevant_chapters = previous_chapters

    # 4. 根据模式构建上下文
    if context_mode == "full":
        return build_full_context(relevant_chapters)
    elif context_mode == "summary":
        return build_summary_context(relevant_chapters)
    else:  # disabled
        return "【这是第一章，直接开始创作】", True
```

### 配置读取

```python
def load_context_config() -> Dict:
    """加载上下文配置"""
    config_file = Path("config/generation_config.json")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return {
                "context_enable": config.get("context_enable", True),
                "context_mode": config.get("context_mode", "summary"),
                "context_max_chapters": config.get("context_max_chapters", 50),
                "context_auto_allocate": config.get("context_auto_allocate", True)
            }
    return DEFAULT_CONTEXT_CONFIG
```

## 使用流程

### 1. 首次使用

1. 启动应用
2. 进入 `系统设置` → `生成参数配置`
3. 在 `上下文管理` 区域设置参数：
   - ✓ 启用上下文机制
   - 选择 `summary` 模式（推荐）
   - 设置 `最大章节数` = 50（可根据需要调整）
   - ✓ 启用自动分配token
4. 点击 `💾 保存配置`
5. 点击 `🧪 测试参数` 查看当前配置

### 2. 开始生成

1. 进入 `小说创作` → `从零开始创作`
2. 填写小说基本信息
3. 点击 `🚀 开始生成`
4. 系统会自动：
   - 读取 `generation_config.json` 中的上下文配置
   - 根据当前章节号计算使用哪些章节
   - 按照配置的模式构建上下文
   - 生成新章节内容

### 3. 调整配置

如果发现：
- **Token消耗太高**：切换到 `summary` 模式或降低 `max_chapters`
- **连贯性不足**：切换到 `full` 模式或提高 `max_chapters`
- **生成速度慢**：切换到 `disabled` 模式测试效果

## 验证配置

运行验证脚本：

```bash
python verify_context_config.py
```

预期输出：
```
✅ 通过 - 配置加载
✅ 通过 - 模式验证
✅ 通过 - 场景模拟
✅ 通过 - 持久化
✅ 所有测试通过！上下文配置系统正常工作
```

## 日志输出

生成过程中的日志示例：

```
第55章使用前50章作为上下文（第6-54章）
摘要模式：使用48个章节摘要
已生成第55章摘要
```

或全文模式：

```
第10章使用前面所有章节（共9章）作为上下文
全文模式：使用9章完整内容，总字符数: 27543
全文模式跳过摘要生成
```

## 技术细节

### Token计算

**摘要模式**（第100章，50章上限）：
- 每个摘要：~50 tokens
- 49个摘要：50 × 49 = 2,450 tokens
- 9个标题：~100 tokens
- **总计：约2,550 tokens**

**全文模式**（第10章）：
- 每章3000字 × 1.5 tokens/字 ≈ 4,500 tokens/chapter
- 9章完整内容：4,500 × 9 = 40,500 tokens
- **总计：约40,500 tokens**

### 性能对比

| 模式 | 第10章 | 第50章 | 第100章 | 100章总token |
|------|--------|--------|---------|--------------|
| summary | ~1K | ~2K | ~2.5K | ~150K |
| full | ~40K | ~200K | ~200K | ~10M |
| disabled | 0 | 0 | 0 | 0 |

## 故障排除

### 问题1：配置不生效

**症状**：修改配置后没有效果

**解决方案**：
1. 点击 `💾 保存配置` 按钮
2. 检查 `config/generation_config.json` 文件是否更新
3. 重启应用

### 问题2：Token消耗仍然很高

**症状**：使用summary模式但token消耗依然很高

**解决方案**：
1. 降低 `max_chapters` 值（如从50降到20）
2. 检查是否误用 `full` 模式
3. 查看日志确认实际使用的模式

### 问题3：连贯性下降

**症状**：角色行为不一致，剧情不连贯

**解决方案**：
1. 切换到 `full` 模式
2. 提高 `max_chapters` 值
3. 确保 `使用连贯性系统` 选项已启用

## 最佳实践

1. **短篇小说（<20章）**：
   - 模式：`full`
   - max_chapters：100（使用所有章节）
   - 追求最高连贯性

2. **中篇小说（20-50章）**：
   - 模式：`summary`
   - max_chapters：30-50
   - 平衡连贯性和成本

3. **长篇小说（50+章）**：
   - 模式：`summary`
   - max_chapters：20-30
   - 优先考虑token成本

4. **测试/原型**：
   - 模式：`disabled`
   - max_chapters：任意
   - 快速迭代

## 未来优化

可能的功能增强：

1. **智能摘要**：AI自动生成更高质量的摘要
2. **动态调整**：根据剩余token自动调整上下文大小
3. **选择性上下文**：只包含相关章节（基于章节相似度）
4. **压缩上下文**：使用压缩算法减少token消耗

## 总结

✅ **配置已统一**：所有上下文配置集中在 `生成参数配置` 页面
✅ **真正可用**：配置会被实际读取和使用，不是摆设
✅ **灵活可调**：支持3种模式、1-100章、可开关
✅ **经过验证**：验证脚本确认系统正常工作
✅ **用户友好**：清晰的UI说明和日志输出

---

最后更新：2026-02-09
版本：AI Novel Generator 4.0
