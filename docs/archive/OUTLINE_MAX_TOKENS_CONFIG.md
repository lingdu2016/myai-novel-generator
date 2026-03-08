# 🔧 大纲生成Max Tokens用户配置功能

**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**

---

## ✅ 已完成修改

### 功能说明

用户现在可以在 **"⚙️ 系统设置" > "🌐 接口管理"** 中手动配置大纲生成时使用的 `max_tokens` 参数。

**位置**：主界面 > 系统设置 > 接口管理 > 大纲生成Max Tokens

**参数范围**：1000 - 32000 tokens
**默认值**：8000 tokens
**推荐值**：
- 10章：4000-6000 tokens
- 30章：8000-10000 tokens
- 50章：12000-16000 tokens
- 100章：20000-32000 tokens

---

## 📝 修改的文件

### 1. `src/ui/app.py`

#### 修改1：添加UI控件（第729-738行）
```python
with gr.Row():
    outline_max_tokens = gr.Slider(
        minimum=1000,
        maximum=32000,
        value=8000,
        step=1000,
        label="大纲生成Max Tokens",
        info="生成大纲时的最大token数，50章建议12000-16000",
        interactive=True
    )
```

#### 修改2：加载配置时读取outline_max_tokens（第772-801行）
```python
def on_provider_change(provider_display):
    # ...其他代码...
    outline_max_val = 8000  # 默认值

    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                for provider in user_config.get("providers", []):
                    if provider.get("provider_id") == config.id:
                        outline_max_val = provider.get("outline_max_tokens", 8000)
                        break

    # 返回时包含outline_max_tokens
    return {
        # ...其他字段...
        outline_max_tokens: outline_max_val,
    }
```

#### 修改3：保存配置时写入outline_max_tokens（第812-862行）
```python
def on_save_config(provider_name, api_key, url, model, timeout_val, outline_max_val, temp, max_tok):
    # ...验证逻辑...

    provider_config = {
        "provider_id": config.id,
        "name": config.name,
        "api_key": api_key,
        "base_url": url if url.strip() else config.base_url,
        "model": model if model.strip() else config.default_model,
        "timeout": int(timeout_val),
        "outline_max_tokens": int(outline_max_val),  # ✅ 保存
        "temperature": temp,
        "max_tokens": max_tok,
        "enabled": True
    }
```

#### 修改4：更新事件绑定（第893-913行）
```python
provider_dropdown.change(
    fn=on_provider_change,
    inputs=[provider_dropdown],
    outputs={custom_url, model_input, timeout_input, outline_max_tokens, max_tokens, api_key_input}
)

save_btn.click(
    fn=on_save_config,
    inputs=[provider_dropdown, api_key_input, custom_url, model_input, timeout_input, outline_max_tokens, temperature, max_tokens],
    outputs=[status_output]
)
```

#### 修改5：初始化自动生成器时读取配置（第166-191行）
```python
def init_auto_generator(self, project_id: Optional[str] = None):
    """初始化自动生成器"""
    # ...其他代码...

    # 读取用户配置中的outline_max_tokens
    outline_max_tokens = 8000  # 默认值
    config_file = Path("config/user_config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 从第一个启用的提供商读取outline_max_tokens配置
                for provider in user_config.get("providers", []):
                    if provider.get("enabled", True):
                        outline_max_tokens = provider.get("outline_max_tokens", 8000)
                        logger.info(f"从配置读取outline_max_tokens: {outline_max_tokens}")
                        break
        except Exception as e:
            logger.warning(f"读取outline_max_tokens配置失败: {e}，使用默认值8000")

    # 创建自动生成器时传入配置
    self.auto_generator = AutoNovelGenerator(
        api_client=self.api_client,
        prompt_manager=self.prompt_manager,
        coherence_system=coherence_system,
        project_dir=self.project_dir,
        outline_max_tokens=outline_max_tokens  # ✅ 传入配置
    )
```

### 2. `src/ui/features/auto_generation.py`

#### 修改1：构造函数添加参数（第30-60行）
```python
def __init__(
    self,
    api_client,
    prompt_manager,
    coherence_system,
    project_dir: Path,
    cache_dir: Optional[Path] = None,
    outline_max_tokens: int = 8000  # ✅ 新增参数
):
    self.api_client = api_client
    self.prompt_manager = prompt_manager
    self.character_tracker = coherence_system.get("character_tracker")
    self.plot_manager = coherence_system.get("plot_manager")
    self.world_db = coherence_system.get("world_db")
    self.project_dir = project_dir
    self.cache_dir = cache_dir or Path("cache/generation")
    self.cache_dir.mkdir(parents=True, exist_ok=True)
    self.outline_max_tokens = outline_max_tokens  # ✅ 保存配置
```

#### 修改2：生成大纲时使用配置的max_tokens（第127-140行）
```python
# 调用API生成
# 使用配置的outline_max_tokens以确保能生成完整的大纲（50章需要约6000-8000 tokens）
logger.info(f"开始生成大纲，使用max_tokens={self.outline_max_tokens}")
response = self.api_client.generate([
    {"role": "system", "content": "你是一个专业的小说大纲创作助手。"},
    {"role": "user", "content": prompt}
], temperature=0.7, max_tokens=self.outline_max_tokens)  # ✅ 使用配置值

if not response:
    logger.error("API返回空响应")
    return False, "AI返回空响应", []

logger.info(f"API响应长度: {len(response)} 字符")
```

---

## 🎯 使用说明

### 如何配置

1. **启动应用**
   ```bash
   python run.py
   ```

2. **进入配置界面**
   - 点击 **"⚙️ 系统设置"** 标签
   - 点击 **"🌐 接口管理"** 子标签
   - 在提供商下拉列表中选择你的API提供商

3. **调整参数**
   - 找到 **"大纲生成Max Tokens"** 滑块
   - 根据需要调整数值：
     - 拖动滑块，或
     - 直接在输入框中输入数值（1000-32000）

4. **保存配置**
   - 点击 **"💾 保存配置"** 按钮
   - 看到提示 "✅ 配置已保存" 即可

### 建议设置

**根据章节数设置：**

| 章节数 | 推荐Max Tokens | 说明 |
|--------|---------------|------|
| 1-10章 | 4000-6000 | 足够生成简短大纲 |
| 11-30章 | 8000-10000 | 可以生成详细大纲 |
| 31-50章 | 12000-16000 | 确保完整生成 |
| 51-100章 | 20000-32000 | 大型小说项目 |

**注意事项：**
- max_tokens越大，API调用成本越高
- 不是所有模型都支持高max_tokens（如GLM-4只支持8192）
- 智谱AI的GLM-4.5-air支持128K，可以设置较高值
- 如果API返回错误，尝试降低max_tokens值

---

## 🧪 测试步骤

### 1. 验证配置加载

**步骤**：
1. 启动应用
2. 进入 "系统设置" > "接口管理"
3. 选择一个提供商
4. 检查 "大纲生成Max Tokens" 是否显示为保存的值

**预期结果**：
- 显示上次保存的配置值
- 默认为8000（如果从未配置过）

### 2. 验证配置生效

**步骤**：
1. 修改 "大纲生成Max Tokens" 为 12000
2. 点击 "保存配置"
3. 进入 "📖 小说创作" > "🚀 自动生成整本小说"
4. 填写信息，生成50章大纲
5. 查看日志

**预期结果**：
- 日志显示：`从配置读取outline_max_tokens: 12000`
- 日志显示：`开始生成大纲，使用max_tokens=12000`
- 大纲成功生成，包含完整的50章

### 3. 验证不同配置

**步骤**：
1. 设置max_tokens=4000，尝试生成50章（应该失败或被截断）
2. 设置max_tokens=16000，尝试生成50章（应该成功）

**预期结果**：
- 低配置时可能被截断
- 高配置时完整生成

---

## 📊 配置文件格式

配置保存在 `config/user_config.json`：

```json
{
  "providers": [
    {
      "provider_id": "zhipu_glm",
      "name": "智谱AI GLM",
      "api_key": "your-api-key",
      "base_url": "https://open.bigmodel.cn/api/paas/v4/",
      "model": "glm-4.5-air",
      "timeout": 60,
      "outline_max_tokens": 12000,  // ✅ 大纲生成的token限制
      "temperature": 0.9,
      "max_tokens": 4000,
      "enabled": true
    }
  ]
}
```

---

## 🔍 故障排查

### 问题1：修改后没有生效

**可能原因**：
- 配置没有保存成功
- 自动生成器在保存前就已初始化

**解决方法**：
1. 确认看到 "✅ 配置已保存" 提示
2. 重启应用，让自动生成器重新加载配置

### 问题2：API返回错误

**可能原因**：
- max_tokens超过了模型的最大限制
- 模型不支持高token输出

**解决方法**：
1. 检查模型的token限制
2. 降低max_tokens值
3. 考虑更换支持更高token的模型

### 问题3：大纲仍然被截断

**可能原因**：
- 虽然增加了max_tokens，但仍然不够

**解决方法**：
1. 继续增加max_tokens值
2. 减少章节数
3. 分批生成大纲

---

## 📈 性能影响

**API响应时间**：
- max_tokens越大，响应时间越长
- 8000 tokens ≈ 10-20秒
- 16000 tokens ≈ 20-40秒

**API成本**：
- 智谱AI GLM-4.5-air: ¥1/百万tokens（输入），¥2/百万tokens（输出）
- 生成50章大纲（约12000 tokens输出）≈ ¥0.024
- 成本影响很小，主要是时间成本

---

## ✅ 后续优化建议

1. **自动计算推荐值**：根据章节数自动推荐合适的max_tokens
2. **实时预览**：显示预计的token消耗和成本
3. **智能调整**：如果检测到截断，自动增加max_tokens并重试
4. **批量生成模式**：当单次无法完成时，自动分批生成

---

**实现日期**: 2026-02-09
**实现人员**: Claude AI
**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**
