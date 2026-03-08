# 🔧 Gradio API 兼容性修复

**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**

---

## 问题说明

应用成功启动后，发现缓存管理功能遇到 Gradio API 兼容性问题：

**错误信息**:
```
TypeError: Dataframe.__init__() got an unexpected keyword argument 'columns'
```

**影响范围**:
- 缓存管理 > 生成缓存刷新功能
- 缓存管理 > 摘要缓存刷新功能

---

## 修复内容

### 问题原因

在新版本 Gradio 中，`gr.DataFrame()` 组件的初始化方式发生了变化：
- **旧版本**: 支持 `gr.DataFrame(columns=[...])` 来创建空表格
- **新版本**: 不再支持 `columns` 参数，需要使用 `pd.DataFrame()` 或 `None`

### 修复方案

将所有的 `gr.DataFrame(columns=...)` 替换为 `pd.DataFrame(columns=...)`

**修改文件**: `src/ui/features/cache_manager.py`

**修改位置**:
1. ✅ Line 262: `on_refresh_caches()` - 空缓存返回值
2. ✅ Line 284: `on_refresh_caches()` - 异常处理返回值
3. ✅ Line 322: `on_refresh_summaries()` - 空缓存返回值
4. ✅ Line 342: `on_refresh_summaries()` - 异常处理返回值

**修复示例**:

```python
# ❌ 旧代码（不兼容）
return (
    gr.DataFrame(columns=["项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
    "暂无生成缓存",
    get_generation_cache_size()
)

# ✅ 新代码（兼容）
import pandas as pd
return (
    pd.DataFrame(columns=["项目名", "当前章节", "总章节", "状态", "缓存时间", "大小(KB)"]),
    "暂无生成缓存",
    get_generation_cache_size()
)
```

---

## Gradio API 变更总结

### 本次修复涉及的 API 变更

| 旧版本 API | 新版本 API | 状态 |
|------------|------------|------|
| `gr.Listbox()` | `gr.Dropdown()` | ✅ 已修复 |
| `gr.DataFrame(columns=...)` | `pd.DataFrame(columns=...)` | ✅ 已修复 |

### API 兼容性处理建议

1. **DataFrame 组件**:
   - 使用 `pd.DataFrame()` 创建数据
   - 返回给 Gradio 组件时会自动转换

2. **列表选择组件**:
   - 使用 `gr.Dropdown()` 替代 `gr.Listbox()`
   - 设置 `multiselect=False` 保持单选行为

---

## 测试验证

### 语法检查
```bash
✓ python -m py_compile src/ui/features/cache_manager.py
```

### 功能验证
- [ ] 缓存管理 > 生成缓存 > 刷新列表
- [ ] 缓存管理 > 摘要缓存 > 刷新列表
- [ ] 缓存管理 > 清理缓存功能

---

## 完整修复记录

### 第一轮修复：启动错误
- ✅ 修复导入路径：`from ..features` → `from .features`
- ✅ 修复 `gr.Listbox` → `gr.Dropdown` (2处)

### 第二轮修复：重复标签
- ✅ 重新组织UI标签结构
- ✅ 移除重复的导出功能
- ✅ 添加风格选择功能

### 第三轮修复：事件绑定错误
- ✅ 删除旧的事件处理代码（export_current_btn等）

### 第四轮修复：DataFrame API (本次)
- ✅ 修复 `gr.DataFrame(columns=...)` → `pd.DataFrame(columns=...)` (4处)

---

## 当前状态

✅ **应用状态**: 成功启动并运行
✅ **URL**: http://127.0.0.1:7860
✅ **所有已知问题**: 已修复

---

## 后续建议

1. **添加Gradio版本锁定**:
   ```bash
   pip install gradio==4.x.x  # 锁定测试通过的版本
   ```

2. **添加版本检查**:
   ```python
   import gradio as gr
   if gr.__version__ < "4.0.0":
       logger.warning(f"Gradio版本过低: {gr.__version__}")
   ```

3. **单元测试**:
   - 为关键功能添加单元测试
   - 测试不同Gradio版本的兼容性

---

**修复日期**: 2026-02-08
**修复人员**: Claude AI
**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**
