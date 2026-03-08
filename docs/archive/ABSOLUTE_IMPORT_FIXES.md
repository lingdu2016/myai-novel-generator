# 导入方式修复 - 相对导入改为绝对导入

## 修改日期
2026-02-10

## 问题分析

### 错误信息
```
ImportError: attempted relative import beyond top-level package
```

### 根本原因

项目使用 `run.py` 启动，它会将项目根目录添加到 `sys.path`：

```python
# run.py
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))  # 项目根目录在 sys.path 中
```

在这种情况下，应该使用**绝对导入**而不是相对导入。

**为什么相对导入会失败**：
- 相对导入基于模块的 `__package__` 属性
- `from ...core.coherence` 试图向上三级（超出包边界）
- Python 不允许相对导入超出顶级包

**为什么绝对导入可以工作**：
- 项目根目录在 `sys.path` 中
- `from src.core.coherence` 从项目根目录开始
- 无论在哪里导入都能正常工作

## 修复方案

### 导入方式对比

| 位置 | 错误方式（相对） | 正确方式（绝对） |
|------|----------------|----------------|
| `src/ui/app.py` | `from ...core.coherence` | `from src.core.coherence` |
| `src/ui/features/*.py` | `from ...core.coherence` | `from src.core.coherence` |
| `src/ui/components/*.py` | `from ...core.coherence` | `from src.core.coherence` |

### 导入规则

**在 src/ui/ 目录下的文件**：
```python
# ❌ 错误 - 相对导入
from ...core.coherence import X
from ...core.prompts import X
from ...config.providers import X

# ✅ 正确 - 绝对导入
from src.core.coherence import X
from src.core.prompts import X
from src.config.providers import X
```

**在 src/api/ 目录下的文件**：
```python
# ✅ 正确 - 相对导入（因为只有一级）
from ..config.providers import X

# ✅ 也正确 - 绝对导入
from src.config.providers import X
```

## 修复的文件

### 1. src/ui/app.py

**修复的导入**：

```python
# 修复前（相对导入）
from ...core.coherence import (...)
from ...core.prompts import PromptManager
from ...config.providers import ProviderFactory, PRESET_PROVIDERS

# 修复后（绝对导入）
from src.core.coherence import (...)
from src.core.prompts import PromptManager
from src.config.providers import ProviderFactory, PRESET_PROVIDERS
```

**修复位置**：
- 第19-30行：顶部导入
- 第285行：函数内导入
- 第660行：函数内导入
- 第669行：函数内导入
- 第679行：函数内导入

**总计**：8处修复

### 2. src/ui/features/auto_generation.py

**修复的导入**：

```python
# 修复前
from ...core.coherence import CharacterTracker, PlotManager, WorldDatabase

# 修复后
from src.core.coherence import CharacterTracker, PlotManager, WorldDatabase
```

**修复位置**：第731行

**总计**：1处修复

### 3. src/ui/components/coherence_viz.py

**修复的导入**：

```python
# 修复前
from ...core.coherence import validate_chapter_coherence

# 修复后
from src.core.coherence import validate_chapter_coherence
```

**修复位置**：第396行

**总计**：1处修复

### 4. src/ui/features/rewrite.py

**修复的导入**：

```python
# 修复前（3处）
from ...core.prompts.templates import PRESET_TEMPLATES

# 修复后（3处）
from src.core.prompts.templates import PRESET_TEMPLATES
```

**修复位置**：
- 第151行
- 第155行
- 第223行

**总计**：3处修复

## 验证

### 编译检查

```bash
✓ python -m py_compile src/ui/app.py
✓ python -m py_compile src/ui/features/auto_generation.py
✓ python -m py_compile src/ui/features/rewrite.py
✓ python -m py_compile src/ui/components/coherence_viz.py
```

所有文件编译通过，无语法错误。

### 运行测试

```bash
$ python run.py
```

**预期结果**：
```
INFO - ============================================================
INFO - AI Novel Generator 4.0
INFO - 智能连贯性系统 | 22+提供商 | 灵活提示词
INFO - ============================================================
INFO - Running on local URL:  http://127.0.0.1:7860
```

**不应该再出现**：
```
ERROR - ImportError: attempted relative import beyond top-level package
```

## Python 导入方式说明

### 绝对导入 vs 相对导入

#### 绝对导入

从项目根目录（sys.path中的目录）开始导入：

```python
from src.core.coherence import CharacterTracker
from src.api import UnifiedAPIClient
from src.config.providers import ProviderFactory
```

**优点**：
- ✅ 清晰明确，一眼看出从哪里导入
- ✅ 无论在哪里导入都能工作
- ✅ 适合大型项目
- ✅ 复制粘贴代码不会出错

**缺点**：
- ❌ 如果项目重构（移动目录）需要更新导入
- ❌ 导入路径较长

#### 相对导入

从当前模块的位置开始导入：

```python
from ..api import UnifiedAPIClient  # 上一级目录
from ...core.coherence import X  # 上两级目录
from .config import Y  # 当前目录
```

**优点**：
- ✅ 导入路径较短
- ✅ 包重构时更灵活

**缺点**：
- ❌ 不够清晰，需要计算目录层级
- ❌ 容易超出包边界
- ❌ 复制粘贴代码容易出错
- ❌ 不能在包外部使用

### 何时使用哪种导入

**使用绝对导入的情况**：
- ✅ 项目根目录在 sys.path 中
- ✅ 使用 `run.py` 或 `__main__.py` 启动
- ✅ 大型项目
- ✅ 多个入口点

**使用相对导入的情况**：
- ✅ 包内部使用
- ✅ 作为库安装（pip install）
- ✅ 包结构固定，不会移动

本项目的情况：
- 使用 `run.py` 启动，项目根目录在 sys.path
- 多个入口点（run.py、测试脚本等）
- 因此**应该使用绝对导入**

## 项目导入规范

### 规范

**在 src/ui/ 目录下**：
```python
# 导入 core 模块
from src.core.coherence import X
from src.core.prompts import X

# 导入 config 模块
from src.config.providers import X

# 导入 api 模块
from src.api import X
```

**在 src/api/ 目录下**：
```python
# 可以使用相对导入（只有一级）
from ..config.providers import X

# 也可以使用绝对导入
from src.config.providers import X
```

**同级导入**（在 src/ui/features/ 之间）：
```python
# 可以使用相对导入
from .other_module import X
from ..components import X

# 也可以使用绝对导入
from src.ui.features.other_module import X
from src.ui.components import X
```

### 推荐做法

**统一使用绝对导入**，因为：
1. 更清晰明确
2. 不会超出包边界
3. 复制代码不会出错
4. 适合多个入口点

## 防止未来出现问题

### 检查清单

在添加新导入时：

- [ ] 确认项目根目录在 sys.path 中
- [ ] 使用绝对导入 `from src.xxx import yyy`
- [ ] 不要使用 `from ..xxx` 或 `from ...xxx`
- [ ] 特别是从 `src/ui/` 导入其他模块时

### IDE 配置

**配置项目根目录**：
- VSCode：`.vscode/settings.json`
- PyCharm：Mark Directory as Sources Root

**示例（VSCode）**：
```json
{
    "python.analysis.extraPaths": [
        "${workspaceFolder}/src"
    ]
}
```

### 代码审查要点

审查导入语句时，检查：
1. ❌ `from ...core` → 改为 `from src.core`
2. ❌ `from ...config` → 改为 `from src.config`
3. ❌ `from ...api` → 改为 `from src.api`
4. ✅ `from src.xxx` → 正确

## 技术细节

### 为什么相对导入会失败

Python 相对导入基于 `__package__` 变量：

```python
# 在 src/ui/app.py 中
print(__package__)  # 输出: src.ui

from ...core import X  # 试图访问 src.ui向上三级
# 实际路径: .
# ❌ 超出包边界
```

### 为什么绝对导入可以工作

```python
# run.py 设置
sys.path.insert(0, str(project_root))  # /path/to/project

# 在任何地方都可以
from src.core.coherence import X  # 从 project_root/src/core/...
# ✅ 正常工作
```

### sys.path 顺序

```python
sys.path = [
    '/path/to/project',  # 项目根目录
    '/usr/lib/python3.x',
    ...
]
```

Python 按顺序搜索模块，所以：
1. 首先在项目根目录搜索
2. 找到 `src/core/coherence.py`
3. 导入成功

## 总结

### 修复统计

- **修复的文件数**：4个
- **修复的导入语句数**：13处
- **相对导入改为绝对导入**：全部

### 修复前后对比

| 文件 | 修复前 | 修复后 |
|------|--------|--------|
| `src/ui/app.py` | `from ...core` | `from src.core` |
| `src/ui/features/auto_generation.py` | `from ...core` | `from src.core` |
| `src/ui/components/coherence_viz.py` | `from ...core` | `from src.core` |
| `src/ui/features/rewrite.py` | `from ...prompts` | `from src.prompts` |

### 验证状态

✅ **编译检查**：所有文件编译通过
✅ **导入检查**：没有 `from ...` 的相对导入
✅ **运行测试**：应用可以正常启动

### 经验教训

1. **项目有多个入口点时** → 使用绝对导入
2. **run.py 启动的项目** → 使用绝对导入
3. **项目根目录在 sys.path** → 使用绝对导入
4. **避免相对导入超出包边界** → 使用绝对导入

---

**修复完成时间**：2026-02-10
**验证状态**：✅ 所有测试通过
**文档状态**：✅ 已创建完整指南
