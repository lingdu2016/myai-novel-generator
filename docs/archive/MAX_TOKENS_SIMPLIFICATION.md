# 🔧 Max Tokens配置简化说明

**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**

---

## ✅ 已完成的简化

### 问题
之前有两个max_tokens设置：
1. **大纲生成Max Tokens** - 专门用于大纲生成
2. **单章生成Max Tokens** - 用于章节生成

这导致设置复杂且容易混淆。

### 解决方案
**简化为单一的全局Max Tokens设置**，所有API调用（大纲生成、章节生成等）都使用这个统一配置。

---

## 📝 修改内容

### 1. UI界面简化

**之前**：
```
高级设置 >
├── 大纲生成Max Tokens (1000-32000, 默认8000)
├── Temperature (0-2, 默认0.8)
└── 单章生成Max Tokens (100-32000, 默认4000)
```

**现在**：
```
高级设置 >
├── Temperature (0-2, 默认0.8)
└── Max Tokens（全局）(100-32000, 默认8000)
```

### 2. 配置文件自动迁移

应用启动时会自动清理旧的`outline_max_tokens`字段：

```python
# 迁移前
{
  "providers": [{
    "outline_max_tokens": 20000,  # ← 旧字段
    "max_tokens": 31300
  }]
}

# 迁移后
{
  "providers": [{
    "max_tokens": 31300  # ← 保留较大值
  }]
}
```

### 3. 代码更新

#### `src/ui/app.py`
- 删除了`outline_max_tokens_input`滑块
- 修改`max_tokens`标签为"Max Tokens（全局）"
- 默认值从4000提高到8000（更适合大纲生成）
- 删除`on_save_config`中的`outline_max_val`参数
- 保存配置后自动重新初始化`auto_generator`
- 添加启动时的配置迁移逻辑

#### `src/ui/features/auto_generation.py`
- 更新注释说明`outline_max_tokens`参数现在接收全局配置值
- 日志会显示实际使用的max_tokens值

---

## 🎯 使用说明

### 配置Max Tokens

1. **进入配置**
   - 点击 **"⚙️ 系统设置"** > **"🌐 接口管理"**
   - 选择你的API提供商

2. **设置Max Tokens**
   - 展开 **"高级设置"**
   - 调整 **"Max Tokens（全局）"** 滑块
   - 范围：100 - 32000
   - 默认：8000

3. **保存配置**
   - 点击 **"💾 保存配置"**
   - **会自动重新初始化生成器**，新配置立即生效

### 推荐设置

| 用途 | 推荐Max Tokens | 说明 |
|------|---------------|------|
| 短篇（1-10章） | 4000-6000 | 足够生成简短大纲和章节 |
| 中篇（11-30章） | 8000-12000 | 平衡性能和质量 |
| 长篇（31-50章） | 12000-16000 | 确保大纲完整生成 |
| 超长篇（50+章） | 20000-32000 | 大型项目需要 |

### 注意事项

⚠️ **Max Tokens越大，响应时间越长**
- 8000 tokens ≈ 10-20秒
- 16000 tokens ≈ 20-40秒
- 32000 tokens ≈ 40-80秒

⚠️ **检查模型限制**
- GLM-4: 最大8192 tokens
- GLM-4.5-air: 最大128000 tokens ✅
- GPT-4o-mini: 最大128000 tokens ✅

---

## 🔄 迁移步骤

### 对于已保存配置的用户

1. **启动应用**
   ```bash
   python run.py
   ```

2. **查看日志**
   - 如果看到 "迁移配置：删除outline_max_tokens字段"，说明自动迁移成功
   - 旧配置会被保留（使用较大值）

3. **验证配置**
   - 进入 **"⚙️ 系统设置"** > **"🌐 接口管理"**
   - 检查 **"Max Tokens（全局）"** 是否显示正确的值

### 手动调整（可选）

如果自动迁移的值不合适：
1. 调整 **"Max Tokens（全局）"** 滑块
2. 点击 **"💾 保存配置"**
3. 重新开始生成

---

## 📊 技术细节

### 为什么这样简化？

1. **用户体验** - 减少混淆，一个设置控制所有生成
2. **代码简洁** - 减少重复逻辑，易于维护
3. **配置清晰** - 不需要区分"大纲"和"章节"的token

### 工作原理

```
用户设置Max Tokens → 保存到配置文件
                     ↓
         init_auto_generator()读取配置
                     ↓
         传给AutoNovelGenerator.outline_max_tokens
                     ↓
         generate_outline()使用self.outline_max_tokens
```

### 配置流程

```python
# 1. 用户在UI设置max_tokens = 20000
# 2. 点击保存
on_save_config() → 保存到user_config.json

# 3. 自动重新初始化
app_state.init_auto_generator()
  └─ 读取max_tokens = 20000
  └─ 创建AutoNovelGenerator(outline_max_tokens=20000)

# 4. 生成大纲时
generate_outline() → max_tokens=self.outline_max_tokens (20000)
```

---

## ✅ 验证清单

- [ ] 启动应用，查看日志确认配置迁移成功
- [ ] 进入"系统设置" > "接口管理"，确认只显示一个Max Tokens滑块
- [ ] 调整Max Tokens值并保存
- [ ] 开始生成大纲，查看日志显示的max_tokens值
- [ ] 确认生成的大纲完整（没有被截断）

---

## 🐛 故障排查

### 问题1：修改后还是用旧值

**原因**：auto_generator没有重新初始化

**解决**：
1. 点击"💾 保存配置"会自动重新初始化
2. 或者重启应用

### 问题2：配置文件迁移失败

**原因**：配置文件格式错误或权限问题

**解决**：
1. 备份配置文件
2. 手动删除`outline_max_tokens`字段
3. 保留`max_tokens`字段

### 问题3：大纲仍然被截断

**原因**：max_tokens不够大

**解决**：
1. 增加Max Tokens值
2. 减少章节数
3. 检查模型是否支持高token输出

---

**更新日期**: 2026-02-09
**更新人员**: Claude AI
**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**
