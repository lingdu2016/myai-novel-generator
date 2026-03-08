# 🔧 大纲生成JSON解析错误修复

**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**

---

## 🐛 问题诊断

### 错误信息
```
生成大纲失败: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

### 问题原因

智谱AI（GLM）模型返回的内容不是纯JSON格式，可能包含：
1. Markdown代码块标记（如 ```json ... ```）
2. 额外的说明文字
3. 格式不正确的JSON

**示例错误响应**:
```
好的，这是为您生成的大纲：

```json
{
  "title": "星河彼岸中",
  "chapters": [...]
}
```

希望这个大纲对您有帮助！
```

而不是纯JSON：
```json
{
  "title": "星河彼岸中",
  "chapters": [...]
}
```

---

## ✅ 修复方案

### 1. 改进提示词

**修改位置**: `src/ui/features/auto_generation.py` 第90-127行

**关键改进**:
1. 明确要求只返回JSON，不要其他文字
2. 提供清晰的格式示例
3. 强调不要markdown标记

**修改后的提示词关键部分**:
```
**重要**：请只返回JSON格式的数据，不要包含任何其他文字、说明或markdown标记。

返回格式示例（不要包含```json标记）：
{{
    "title": "{title}",
    "chapters": [...]
}}

请直接返回JSON数据，开头不要有任何文字。
```

### 2. 增强JSON解析

**修改位置**: `src/ui/features/auto_generation.py` 第127-147行

**多层解析策略**:

**步骤1**: 直接解析
```python
try:
    result = json.loads(response)
except json.JSONDecodeError:
    # 进入步骤2
```

**步骤2**: 清理后解析
```python
# 去除markdown代码块标记
if cleaned_response.startswith("```json"):
    cleaned_response = cleaned_response[7:]
elif cleaned_response.startswith("```"):
    cleaned_response = cleaned_response[3:]
if cleaned_response.endswith("```"):
    cleaned_response = cleaned_response[:-3]
cleaned_response = cleaned_response.strip()

try:
    result = json.loads(cleaned_response)
except json.JSONDecodeError:
    # 进入步骤3
```

**步骤3**: 正则提取JSON
```python
json_match = re.search(r'\{[\s\S]*\}', cleaned_response)
if json_match:
    result = json.loads(json_match.group(0))
else:
    # 完全失败
    logger.error(f"无法解析JSON。原始响应: {response[:1000]}")
    return False, "无法解析AI返回的大纲（JSON格式错误）", []
```

### 3. 添加详细日志

**日志内容**:
```python
logger.debug(f"API原始响应（前500字符）: {response[:500]}...")
logger.debug(f"清理后的响应（前500字符）: {cleaned_response[:500]}...")
logger.info("清理后成功解析JSON")
logger.info("通过正则提取成功解析JSON")
logger.error(f"无法解析JSON。原始响应: {response[:1000]}")
```

**日志用途**:
- 帮助诊断API返回内容的格式
- 了解哪种解析方法成功
- 在完全失败时提供调试信息

---

## 🎯 使用建议

### 1. 重启应用

```bash
python .\run.py
```

### 2. 再次尝试生成大纲

1. 进入"🚀 自动生成整本小说"
2. 填写小说信息
3. 点击"🚀 开始生成"
4. 查看日志确认解析成功

**成功日志**:
```
INFO - 开始生成大纲: 星河彼岸中 (50章)
DEBUG - API原始响应（前500字符）: {"title": "星河彼岸中"...
DEBUG - 清理后的响应（前500字符）: {"title": "星河彼岸中"...
INFO - 清理后成功解析JSON
INFO - 大纲生成成功，共 50 章
```

### 3. 如果仍然失败

**查看日志**:
```bash
tail -100 logs/debug_20260209.log | grep "API原始响应\|清理后响应"
```

**可能的原因**:
1. API返回了错误消息（而不是大纲）
2. 模型不支持生成JSON格式
3. 提示词太长导致截断

**解决方法**:
1. 尝试使用不同的模型（如 `glm-4-flash`）
2. 减少章节数（从50章改为10章测试）
3. 增加超时时间（已在上一个修复中实现）

---

## 📋 修改文件

| 文件 | 修改内容 | 说明 |
|------|---------|------|
| `src/ui/features/auto_generation.py` | 1. 改进提示词，明确要求纯JSON<br>2. 增强JSON解析逻辑（3层处理）<br>3. 添加详细调试日志 | +50行 |

---

## ✅ 验证清单

- [ ] 重启应用
- [ ] 生成小说大纲
- [ ] 查看日志显示 "清理后成功解析JSON" 或 "通过正则提取成功解析JSON"
- [ ] 大纲成功生成，章节列表正常显示

---

**修复日期**: 2026-02-09
**修复人员**: Claude AI
**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**
