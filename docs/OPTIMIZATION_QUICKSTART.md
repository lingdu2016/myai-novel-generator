# 优化系统快速开始指南

## 🚀 5分钟快速上手

### 1. 确保依赖已安装

```bash
pip install -r requirements.txt
```

### 2. 使用优化生成器

```python
from src.core import create_optimized_generator
from src.core.coherence import CharacterTracker, PlotManager, WorldDatabase, HierarchicalSummaryManager
from src.api import create_api_client

# 初始化API客户端
api_client = create_api_client([
    {
        "provider_id": "openai",
        "api_key": "your-api-key",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4",
        "enabled": True
    }
])

# 初始化连贯性系统
cache_dir = Path("cache/coherence")
character_tracker = CharacterTracker("project_id", cache_dir)
plot_manager = PlotManager("project_id", cache_dir)
world_db = WorldDatabase("project_id", cache_dir)
summary_manager = HierarchicalSummaryManager("project_id", cache_dir)

# 创建优化生成器
generator = create_optimized_generator(
    api_client=api_client,
    summary_manager=summary_manager,
    character_tracker=character_tracker,
    plot_manager=plot_manager,
    world_db=world_db,
    project_dir=Path("projects")
)

# 生成优化章节
success, message, chapter_data = generator.generate_optimized_chapter(
    chapter_num=1,
    chapter_title="第一章",
    chapter_desc="主角醒来，发现自己穿越到了一个陌生的世界...",
    target_words=3000,
    previous_chapters=[]
)

if success:
    print(f"✓ 生成成功！")
    print(f"字数: {chapter_data['word_count']}")
    print(f"质量评分: {chapter_data['quality_report']['total_score']}")
    print(f"风格评分: {chapter_data['optimization_report']['optimized_score']}")
else:
    print(f"✗ {message}")
```

### 3. 查看优化报告

```python
# 质量报告
quality_report = chapter_data['quality_report']
print(f"\n=== 质量评估 ===")
print(f"总分: {quality_report['total_score']} ({quality_report['grade']})")
print(f"连贯性: {quality_report['dimension_scores']['连贯性']['score']}")
print(f"情节: {quality_report['dimension_scores']['情节']['score']}")
print(f"角色: {quality_report['dimension_scores']['角色']['score']}")
print(f"风格: {quality_report['dimension_scores']['风格']['score']}")

# 风格优化报告
style_report = chapter_data['optimization_report']
print(f"\n=== 风格优化 ===")
print(f"原始评分: {style_report['original_score']} ({style_report['original_grade']})")
print(f"优化后评分: {style_report['optimized_score']} ({style_report['optimized_grade']})")
print(f"提升: {style_report['score_improvement']:.1f}")
print(f"检测到问题: {style_report['issues_count']} 个")
```

---

## 🎯 常见用例

### 用例1：单独优化已有文本

```python
from src.core.style_optimizer import detect_and_optimize

# 你已有的文本
original_text = """
突然，他感到一阵强烈的情绪涌上心头！这竟然是他从未体验过的感觉...
在漆黑的夜晚背景下，随着雨越下越大，他不由得陷入了沉思...
"""

# 检测并优化
optimized_text, report = detect_and_optimize(
    content=original_text,
    api_client=api_client,
    use_ai=True  # 使用AI辅助优化
)

print("原始文本:")
print(original_text)
print("\n优化后文本:")
print(optimized_text)
print(f"\n质量提升: {report['score_improvement']:.1f}")
```

### 用例2：评估章节质量

```python
from src.core.quality_assessor import assess_chapter_quality

# 你的章节内容
chapter_content = """
（这里放你的章节内容）
"""

# 评估质量
report = assess_chapter_quality(
    content=chapter_content,
    chapter_num=1,
    chapter_outline="主角醒来，发现自己穿越到了一个陌生的世界",
    previous_summary="",
    api_client=api_client
)

print(f"质量评分: {report['total_score']} ({report['grade']})")
print("\n主要问题:")
for issue in report['overall_issues'][:5]:
    print(f"  - {issue}")

print("\n改进建议:")
for suggestion in report['overall_suggestions'][:5]:
    print(f"  - {suggestion}")
```

### 用例3：批量优化多个章节

```python
from src.core.style_optimizer import StyleOptimizer

optimizer = StyleOptimizer(api_client)

# 你的章节列表
chapters = [
    {"num": 1, "content": "第一章内容..."},
    {"num": 2, "content": "第二章内容..."},
    {"num": 3, "content": "第三章内容..."},
]

# 批量优化
for chapter in chapters:
    optimized, report = optimizer.optimize_with_ai(chapter['content'])
    chapter['optimized_content'] = optimized
    chapter['report'] = report

    print(f"第{chapter['num']}章: {report['original_score']} → {report['optimized_score']} (+{report['score_improvement']:.1f})")
```

---

## ⚙️ 配置选项

### 优化生成器配置

```python
# 创建生成器后，可以调整配置
generator.generation_config = {
    "enable_style_optimization": True,  # 启用风格优化
    "enable_quality_assessment": True,  # 启用质量评估
    "style_optimization_mode": "auto",  # auto/ai_off/ai_on
    "min_quality_score": 70.0,  # 最低质量分数
    "max_optimization_attempts": 2,  # 最大优化尝试次数
}
```

### 风格优化模式说明

- **auto**: 自动模式（推荐）
  - 质量好（≥85分）：仅本地优化
  - 质量一般（<85分）：AI辅助优化

- **ai_off**: 仅本地优化
  - 速度快，成本低
  - 适合快速迭代

- **ai_on**: 强制AI优化
  - 质量最佳，但成本高
  - 适合最终版本

---

## 📊 效果对比

### 优化前

```
突然，他感到一阵强烈的情绪涌上心头！这竟然是他从未体验过的感觉...
在漆黑的夜晚背景下，随着雨越下越大，他不由得陷入了沉思...
这一刻，他终于明白了人生的真谛！
```

**问题：**
- AI味道重（突然、竟然、心中涌起）
- 空洞描写（强烈的情绪、从未体验的感觉）
- 机械表达（在...的背景下、随着...的发展）
- 结尾总结（终于明白人生真谛）

### 优化后

```
他点燃一支烟，烟雾在灯光下缓缓升起。"事情没那么简单。"他没看她。
雨下了一夜。天亮的时候，院子里积了水，漂着几片落叶。
```

**改进：**
- 去掉AI化表达
- 具体描写（点燃一支烟、烟雾升起）
- 对话自然（事情没那么简单）
- 无结尾总结，自然结束

---

## 🔧 故障排查

### 问题1：优化后质量反而下降

**原因：** AI优化可能过度修改原意

**解决：**
```python
# 使用本地优化模式
generator.generation_config["style_optimization_mode"] = "ai_off"
```

### 问题2：生成速度变慢

**原因：** 质量评估增加了时间

**解决：**
```python
# 禁用质量评估
generator.generation_config["enable_quality_assessment"] = False
```

### 问题3：API调用次数过多

**原因：** AI优化模式频繁调用API

**解决：**
```python
# 仅在必要时使用AI优化
generator.generation_config["style_optimization_mode"] = "auto"
```

---

## 📚 更多资源

- [完整优化方案](./OPTIMIZATION_PLAN.md)
- [API文档](../README.md#api文档)
- [问题反馈](https://github.com/yangqi1309134997-coder/ai-novel-generator/issues)

---

**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**
