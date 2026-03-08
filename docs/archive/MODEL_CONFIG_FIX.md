# ✅ 模型配置修复报告

**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**

---

## 🔍 问题分析

### 用户反馈
```
API配置填写的模型是 glm-4.5-air
但系统调用的是默认模型（而不是用户配置的模型）
```

### 根本原因

**代码问题**：
在 `src/api/client.py` 中，`generate()` 方法使用了 `connection.config.default_model` 而不是用户配置的 `model` 字段。

**位置**：
- Line 351: `model = connection.config.default_model`
- Line 496: `model=conn.config.default_model`

**数据流**：
1. 用户配置：`{"model": "glm-4.5-air", ...}`
2. 初始化连接：只保存了 `config`，**忽略了 `model` 字段**
3. 调用API：使用 `config.default_model`（例如 `glm-4`）

---

## ✅ 修复方案

### 修复1: 添加用户模型字段

**文件**: `src/api/client.py`
**类**: `ProviderConnection`

**修改前**:
```python
class ProviderConnection:
    config: ProviderConfig
    client: OpenAI
    api_key: str
    rate_limiter: RateLimiter
    # ❌ 缺少 model 字段
```

**修改后**:
```python
class ProviderConnection:
    config: ProviderConfig
    client: OpenAI
    api_key: str
    rate_limiter: RateLimiter
    model: str  # ✅ 新增：用户配置的模型
```

---

### 修复2: 保存用户配置的模型

**位置**: `_init_connections()` 方法

**修改前**:
```python
connection = ProviderConnection(
    config=preset_config,
    client=client,
    api_key=api_key,
    rate_limiter=rate_limiter
)
# ❌ model 字段被忽略了
```

**修改后**:
```python
# 使用用户配置的模型或默认模型
user_model = config_dict.get("model", preset_config.default_model)

connection = ProviderConnection(
    config=preset_config,
    client=client,
    api_key=api_key,
    rate_limiter=rate_limiter,
    model=user_model  # ✅ 保存用户配置的模型
)
```

---

### 修复3: 优先使用用户模型

**位置**: `generate()` 方法

**修改前**:
```python
# 使用提供商的默认模型
if not model:
    model = connection.config.default_model  # ❌ 总是使用默认模型
```

**修改后**:
```python
# 优先使用用户配置的模型，其次使用默认模型
if not model:
    model = connection.model if hasattr(connection, 'model') else connection.config.default_model
    # ✅ 优先级：用户模型 > 默认模型
```

---

### 修复4: 测试连接也使用用户模型

**位置**: `test_connection()` 方法

**修改前**:
```python
response = conn.client.chat.completions.create(
    model=conn.config.default_model,  # ❌ 使用默认模型
    messages=[{"role": "user", "content": "test"}],
    max_tokens=5
)
```

**修改后**:
```python
test_model = conn.model if hasattr(conn, 'model') else conn.config.default_model
response = conn.client.chat.completions.create(
    model=test_model,  # ✅ 使用用户配置的模型
    messages=[{"role": "user", "content": "test"}],
    max_tokens=5
)
```

---

## 🎯 验证方法

### 1. 查看当前配置

```json
{
  "providers": [
    {
      "provider_id": "zhipu",
      "api_key": "...",
      "model": "glm-4.5-air",  // ✓ 这是您配置的模型
      "enabled": true
    }
  ]
}
```

### 2. 查看日志验证

修复后，日志中应该显示：
```
DEBUG - 调用API: 智谱AI (GLM) model=glm-4.5-air
```

而不是：
```
DEBUG - 调用API: 智谱AI (GLM) model=glm-4  // ✗ 使用了默认模型
```

### 3. 实际测试

1. **重启应用**（必须重启才能生效）
```bash
python .\run.py
```

2. **测试生成功能**
   - 创建项目
   - 生成章节
   - 查看日志，确认使用了正确的模型

---

## 📋 配置示例

### 智谱AI GLM 配置

```json
{
  "providers": [
    {
      "provider_id": "zhipu",
      "name": "智谱AI (GLM)",
      "api_key": "your-api-key",
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "model": "glm-4.5-air",      // ✓ 优先使用此模型
      "temperature": 0.8,
      "max_tokens": 20000,
      "enabled": true
    }
  ]
}
```

### 其他提供商配置示例

**OpenAI**:
```json
{
  "provider_id": "openai",
  "model": "gpt-4o-mini"  // ✓ 使用用户指定的模型
}
```

**阿里通义**:
```json
{
  "provider_id": "alibaba",
  "model": "qwen-max"  // ✓ 使用用户指定的模型
}
```

---

## ⚠️ 重要说明

### 模型优先级

**完整优先级**：
1. **调用时指定**: `generate(..., model="custom-model")`  # 最高优先级
2. **用户配置**: `connection.model` (您在配置文件中填的)
3. **默认模型**: `config.default_model` (预设配置的默认值)

### 配置建议

**推荐做法**：
- ✅ 在配置文件中明确指定 `model` 字段
- ✅ 确保模型名称与提供商支持的模型一致
- ✅ 测试时查看日志，确认使用了正确的模型

**避免**：
- ❌ 不配置 `model` 字段（会使用默认模型）
- ❌ 使用不存在的模型名称
- ❌ 配置与提供商不匹配的模型

---

## 🔧 调试技巧

### 查看实际使用的模型

在日志文件中搜索 `调用API`：
```powershell
Select-String -Path logs\app_20260208.log -Pattern "调用API.*model="
```

**正确输出**:
```
DEBUG - 调用API: 智谱AI (GLM) model=glm-4.5-air
```

### 配置验证

```python
# Python 代码验证
import json
from pathlib import Path

config_file = Path("config/user_config.json")
with open(config_file) as f:
    config = json.load(f)

for provider in config["providers"]:
    print(f"提供商: {provider['name']}")
    print(f"  模型: {provider.get('model', '未配置')}")
    print(f"  启用: {provider.get('enabled', False)}")
```

---

## 📊 修复前后对比

| 场景 | 修复前 | 修复后 |
|------|--------|--------|
| 用户配置 | `model: "glm-4.5-air"` | `model: "glm-4.5-air"` |
| 实际调用 | `model=glm-4` (默认) | `model=glm-4.5-air` (用户配置) |
| 灵活性 | ❌ 固定使用默认模型 | ✅ 尊重用户配置 |
| 优先级 | 无优先级 | 3级优先级系统 |

---

## ✅ 验证清单

重启应用后，请验证：

- [ ] 配置文件中有 `"model": "glm-4.5-air"`
- [ ] 重启应用
- [ ] 生成章节
- [ ] 查看日志：`model=glm-4.5-air`
- [ ] 确认使用了正确的模型

---

**修复日期**: 2026-02-08
**修复人员**: Claude AI
**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**
