# 🔧 超时时间配置功能 - 实现报告

**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**

---

## 📊 问题诊断

### 用户反馈

**原始问题**:
```
API错误: Request timed out.
生成大纲失败: 生成失败，已重试3次: Request timed out.
```

**用户需求**:
> "请问他现在设置的超时时间是多少？为什么用户不能自己设置那个超时时间？请把那个用户自己设置超时时间的这个选项，放到这个接口管理api配置这个下面这样才对。"

### 问题分析

1. **当前超时时间**: 60秒（硬编码在 `src/api/client.py` 第273行）
2. **无法自定义**: 用户界面没有超时时间设置选项
3. **超时原因**: 生成大纲需要较长时间，60秒不够用

**根本原因**:
```python
# src/api/client.py 第270-274行
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
    timeout=60  # ❌ 硬编码，用户无法修改
)
```

---

## ✅ 实现方案

### 1. 添加超时时间滑块

**位置**: `src/ui/app.py` 高级设置折叠面板（第713-746行）

**新增UI组件**:
```python
with gr.Accordion("高级设置", open=False):
    # ... 其他设置 ...

    with gr.Row():
        timeout_input = gr.Slider(
            minimum=10,        # 最小10秒
            maximum=600,       # 最大10分钟（600秒）
            value=60,          # 默认60秒
            step=10,           # 每次调整10秒
            label="请求超时时间（秒）",
            info="API请求的最长等待时间，建议60-180秒",
            interactive=True
        )
```

**UI位置**:
```
⚙️ 系统设置
  └── 🌐 接口管理
      ├── 提供商选择
      ├── API Key输入
      └── 高级设置 (▼)
          ├── 自定义URL
          ├── 模型名称
          ├── 请求超时时间（秒） ← 新增 ✅
          ├── Temperature
          └── Max Tokens
```

---

### 2. 保存超时配置

**修改**: `on_save_config` 函数（第812-862行）

**修改前**:
```python
provider_config = {
    "provider_id": config.id,
    "name": config.name,
    "api_key": api_key,
    "base_url": url if url.strip() else config.base_url,
    "model": model if model.strip() else config.default_model,
    "temperature": temp,
    "max_tokens": max_tok,
    "enabled": True
    # ❌ 没有timeout字段
}
```

**修改后**:
```python
provider_config = {
    "provider_id": config.id,
    "name": config.name,
    "api_key": api_key,
    "base_url": url if url.strip() else config.base_url,
    "model": model if model.strip() else config.default_model,
    "timeout": int(timeout_val),  # ✅ 保存超时时间
    "temperature": temp,
    "max_tokens": max_tok,
    "enabled": True
}
```

**配置文件格式** (`config/user_config.json`):
```json
{
  "providers": [
    {
      "provider_id": "zhipu",
      "name": "智谱AI (GLM)",
      "api_key": "your-api-key",
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "model": "glm-4.5-air",
      "timeout": 180,  // ✅ 新增：超时时间（秒）
      "temperature": 0.8,
      "max_tokens": 4000,
      "enabled": true
    }
  ]
}
```

---

### 3. 使用超时配置

**修改**: `src/api/client.py` `_init_connections` 方法（第265-279行）

**修改前**:
```python
try:
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=60  # ❌ 硬编码60秒
    )
```

**修改后**:
```python
# 使用用户配置的超时时间或默认值（60秒）
user_timeout = config_dict.get("timeout", 60)
try:
    user_timeout = int(user_timeout)
    if user_timeout < 10:
        user_timeout = 10  # 最小10秒
    elif user_timeout > 600:
        user_timeout = 600  # 最大10分钟
except (ValueError, TypeError):
    user_timeout = 60  # 默认60秒

try:
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=user_timeout  # ✅ 使用用户配置的超时时间
    )
```

**验证逻辑**:
- 最小值：10秒（避免过短导致快速失败）
- 最大值：600秒（10分钟，避免过长等待）
- 默认值：60秒
- 自动验证：如果用户输入无效值，使用默认值

---

### 4. 测试连接时使用超时

**修改**: `on_test_connection` 函数（第776-810行）

**修改前**:
```python
def on_test_connection(provider_display, api_key, url, model):
    # ...
    temp_client = create_api_client([{
        "provider_id": config.id,
        "api_key": api_key,
        "base_url": base_url,
        "model": model if model.strip() else config.default_model,
        "enabled": True
        # ❌ 没有timeout参数
    }])
```

**修改后**:
```python
def on_test_connection(provider_display, api_key, url, model, timeout_val):
    # ...
    temp_client = create_api_client([{
        "provider_id": config.id,
        "api_key": api_key,
        "base_url": base_url,
        "model": model if model.strip() else config.default_model,
        "timeout": int(timeout_val),  # ✅ 使用配置的超时时间
        "enabled": True
    }])

    if result:
        return f"✓ 连接测试成功！{config.name} 可用（超时: {timeout_val}秒）"  # ✅ 显示超时时间
```

---

### 5. 切换提供商时加载超时配置

**修改**: `on_provider_change` 函数（第761-774行）

**修改前**:
```python
def on_provider_change(provider_display):
    # ...
    updates = {
        custom_url: config.base_url,
        model_input: config.default_model,
        api_key_input: "" if config.requires_key else "不需要API Key"
    }
    return updates
```

**修改后**:
```python
def on_provider_change(provider_display):
    # ...
    # 尝试从用户配置中读取该提供商的超时时间
    config_file = Path("config/user_config.json")
    timeout_val = 60  # 默认值
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                for provider in user_config.get("providers", []):
                    if provider.get("provider_id") == config.id:
                        timeout_val = provider.get("timeout", 60)
                        break
        except Exception:
            pass

    updates = {
        custom_url: config.base_url,
        model_input: config.default_model,
        timeout_input: timeout_val,  # ✅ 加载保存的超时时间
        api_key_input: "" if config.requires_key else "不需要API Key"
    }
    return updates
```

---

### 6. 更新事件绑定

**修改**: 事件绑定部分（第864-881行）

**修改前**:
```python
test_btn.click(
    fn=on_test_connection,
    inputs=[provider_dropdown, api_key_input, custom_url, model_input],
    outputs=[status_output]
)

save_btn.click(
    fn=on_save_config,
    inputs=[provider_dropdown, api_key_input, custom_url, model_input, temperature, max_tokens],
    outputs=[status_output]
)
```

**修改后**:
```python
test_btn.click(
    fn=on_test_connection,
    inputs=[provider_dropdown, api_key_input, custom_url, model_input, timeout_input],  # ✅ 添加timeout_input
    outputs=[status_output]
)

save_btn.click(
    fn=on_save_config,
    inputs=[provider_dropdown, api_key_input, custom_url, model_input, timeout_input, temperature, max_tokens],  # ✅ 添加timeout_input
    outputs=[status_output]
)
```

---

## 🎯 使用指南

### 1. 配置超时时间

**步骤**:
1. 进入"⚙️ 系统设置"标签
2. 进入"🌐 接口管理"子标签
3. 点击"高级设置"展开折叠面板
4. 找到"请求超时时间（秒）"滑块
5. 调整超时时间：
   - **快速网络**: 60秒（默认）
   - **慢速网络/长文本**: 120-180秒
   - **非常慢的网络**: 300秒（5分钟）
   - **极慢情况**: 600秒（10分钟，最大值）
6. 点击"💾 保存配置"按钮

### 2. 测试超时设置

**步骤**:
1. 配置好超时时间后
2. 点击"🔗 测试连接"按钮
3. 查看状态输出：`✓ 连接测试成功！智谱AI (GLM) 可用（超时: 180秒）`

### 3. 不同场景的建议超时时间

| 场景 | 建议超时 | 说明 |
|------|---------|------|
| 单章生成（2000字） | 60秒 | 默认值，适用于大多数情况 |
| 生成大纲（50章） | 180秒 | 需要较长时间处理 |
| 批量生成（10章） | 300秒 | 多次API调用 |
| 完整小说生成（50+章） | 300-600秒 | 大量API调用，网络波动影响大 |
| 使用本地模型（Ollama） | 30-60秒 | 本地响应快，不需要太长 |

### 4. 超时错误的处理

**如果仍然超时**:
1. **增加超时时间**: 尝试设置为300秒或更多
2. **检查网络**:
   ```bash
   ping open.bigmodel.cn
   ```
3. **检查API状态**: 访问提供商官网查看是否有服务中断
4. **简化请求**:
   - 减少生成字数
   - 降低temperature
   - 使用更快的模型

**错误提示**:
```
API错误: Request timed out.
生成大纲失败: 生成失败，已重试3次: Request timed out.
```

**解决方法**:
1. 将超时时间从60秒增加到180秒
2. 重新保存配置
3. 重新尝试生成

---

## 📁 修改文件清单

| 文件 | 修改内容 | 行数 |
|------|---------|------|
| `src/ui/app.py` | 1. 添加超时时间滑块UI<br>2. 修改`on_save_config`保存timeout<br>3. 修改`on_test_connection`使用timeout<br>4. 修改`on_provider_change`加载timeout<br>5. 更新事件绑定 | +30行 |
| `src/api/client.py` | 1. 从配置读取timeout<br>2. 验证timeout范围（10-600秒）<br>3. 使用timeout创建OpenAI客户端 | +15行 |

---

## 🔄 配置文件示例

### 完整的用户配置文件

**路径**: `config/user_config.json`

```json
{
  "providers": [
    {
      "provider_id": "zhipu",
      "name": "智谱AI (GLM)",
      "api_key": "your-api-key-here",
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "model": "glm-4.5-air",
      "timeout": 180,
      "temperature": 0.8,
      "max_tokens": 4000,
      "enabled": true
    }
  ]
}
```

### 手动编辑配置文件

如果需要手动编辑：
1. 打开 `config/user_config.json`
2. 找到对应的提供商配置
3. 添加或修改 `"timeout": 180`
4. 保存文件
5. 重启应用

---

## ✅ 验证清单

重启应用后，请验证：

- [ ] 进入"⚙️ 系统设置" > "🌐 接口管理"
- [ ] 展开"高级设置"
- [ ] 看到"请求超时时间（秒）"滑块
- [ ] 默认值显示为60秒
- [ ] 可以拖动滑块调整超时时间（10-600秒）
- [ ] 点击"💾 保存配置"，状态显示超时时间
- [ ] 点击"🔗 测试连接"，状态显示超时时间
- [ ] 生成大纲时不再超时（如果设置了足够大的超时时间）
- [ ] 查看 `config/user_config.json` 包含 `"timeout": xxx`

---

## ⚠️ 重要说明

### 超时时间的影响

**超时时间太短**（如10秒）:
- ❌ 所有请求都超时
- ❌ 无法生成任何内容
- ❌ 用户体验极差

**超时时间太长**（如600秒）:
- ✅ 可以处理长时间请求
- ⚠️ 但失败时需要等待很长时间才能知道
- ⚠️ 可能导致UI长时间无响应

**建议平衡**:
- **测试连接**: 60秒（足够测试是否可用）
- **正常生成**: 120-180秒（适用于大多数情况）
- **批量生成**: 300秒（可以处理多章生成）
- **完整小说**: 300-600秒（根据网络情况调整）

### 自动重试机制

系统已经有自动重试机制：
- 最多重试3次
- 每次重试都会等待一段时间（指数退避）
- 如果超时时间设置合理，大多数请求会成功

**重试日志**:
```
openai._base_client - INFO - Retrying request to /chat/completions in 0.441331 seconds
```

---

**实现日期**: 2026-02-08
**实现人员**: Claude AI
**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**
