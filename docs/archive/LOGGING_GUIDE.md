# 📋 日志系统使用说明

**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**

---

## 日志文件位置

所有日志文件存放在项目根目录的 `logs/` 文件夹中：

```
ai-novel-generator-4.0/
└── logs/
    ├── app_20260208.log          # 主日志（所有级别）
    ├── error_20260208.log        # 错误日志（仅ERROR级别）
    └── ...
```

---

## 日志文件类型

### 1. 主日志文件
**文件名**: `app_YYYYMMDD.log`
**包含**: 所有级别的日志（DEBUG, INFO, WARNING, ERROR, CRITICAL）
**用途**:
- 完整的应用运行记录
- 调试信息
- 功能执行轨迹

### 2. 错误日志文件
**文件名**: `error_YYYYMMDD.log`
**包含**: 仅ERROR级别及以上
**用途**:
- 快速定位错误
- 错误追踪和分析
- 生产环境问题排查

---

## 日志格式

每条日志记录包含以下信息：

```
2026-02-08 18:30:00 - src.ui.app - INFO - 应用启动成功
│                 │         │       │      └─ 日志消息
│                 │         │       └─ 日志级别
│                 │         └─ 模块名称
│                 └─ 时间戳
└─ 日期
```

---

## 日志级别

| 级别 | 用途 | 示例 |
|------|------|------|
| **DEBUG** | 详细调试信息 | 函数参数、中间变量值 |
| **INFO** | 一般信息 | 功能开始/完成、状态更新 |
| **WARNING** | 警告信息 | API调用失败但可恢复 |
| **ERROR** | 错误信息 | 功能失败、异常捕获 |
| **CRITICAL** | 严重错误 | 应用无法继续运行 |

---

## 代码中使用日志

### 基本用法

```python
import logging

logger = logging.getLogger(__name__)

# 不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 带异常的日志

```python
try:
    # 一些操作
    pass
except Exception as e:
    logger.error(f"操作失败: {e}", exc_info=True)
    # exc_info=True 会记录完整的堆栈跟踪
```

### 格式化日志

```python
user_id = 123
action = "登录"
logger.info(f"用户 {user_id} 执行 {action} 操作")
# 输出: 用户 123 执行 登录 操作
```

---

## 查看日志

### 实时查看日志（Windows PowerShell）

```powershell
# 查看主日志
Get-Content logs\app_20260208.log -Wait -Tail 50

# 查看错误日志
Get-Content logs\error_20260208.log -Wait -Tail 50
```

### 实时查看日志（Linux/Mac/WSL）

```bash
# 查看主日志
tail -f logs/app_20260208.log

# 查看错误日志
tail -f logs/error_20260208.log

# 查看最近50行
tail -n 50 logs/app_20260208.log
```

### 搜索特定内容

```powershell
# 搜索错误
Select-String -Path logs\app_20260208.log -Pattern "ERROR"

# 搜索特定模块
Select-String -Path logs\app_20260208.log -Pattern "cache_manager"
```

```bash
# 搜索错误
grep "ERROR" logs/app_20260208.log

# 搜索特定模块
grep "cache_manager" logs/app_20260208.log
```

---

## 日志管理

### 日志轮转

当前版本每天创建一个新日志文件。建议定期清理旧日志：

```bash
# Windows PowerShell
# 删除7天前的日志
Get-ChildItem logs\*.log | Where-Object LastWriteTime -lt (Get-Date).AddDays(-7) | Remove-Item

# Linux/Mac/WSL
# 删除7天前的日志
find logs/ -name "*.log" -mtime +7 -delete
```

### 日志文件大小

如果需要限制日志文件大小，可以修改 `src/ui/app.py` 中的日志配置，使用 `RotatingFileHandler`：

```python
from logging.handlers import RotatingFileHandler

# 限制单个日志文件为10MB，最多保留5个备份
file_handler = RotatingFileHandler(
    main_log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
```

---

## 常见问题排查

### 问题1：日志目录不存在
**症状**: 启动时报错 "No such file or directory: 'logs'"
**解决**: 应用会自动创建 logs 目录

### 问题2：日志文件为空
**症状**: 日志文件存在但没有内容
**解决**: 检查日志级别设置，确保有日志输出

### 问题3：日志文件过大
**症状**: 日志文件占用大量磁盘空间
**解决**:
1. 定期清理旧日志
2. 配置日志轮转
3. 调整日志级别（减少DEBUG日志）

---

## 日志最佳实践

### 1. 合理使用日志级别

```python
# ✅ 好的做法
logger.info("用户登录成功")
logger.warning("API调用缓慢，耗时5秒")
logger.error("数据库连接失败", exc_info=True)

# ❌ 不好的做法
logger.critical("用户登录成功")  # 不应该用CRITICAL级别
logger.debug("每条循环迭代")    # 循环中的DEBUG日志会产生大量输出
```

### 2. 包含上下文信息

```python
# ✅ 好的做法
logger.error(f"生成章节失败 - 项目:{project_id}, 章节:{chapter_num}, 错误:{str(e)}")

# ❌ 不好的做法
logger.error("生成章节失败")  # 缺少上下文信息
```

### 3. 敏感信息处理

```python
# ✅ 好的做法 - 隐藏API密钥
api_key = "sk-xxxxx"
logger.info(f"使用API密钥: {api_key[:8]}...")  # 只显示前8个字符

# ❌ 不好的做法 - 完整记录敏感信息
logger.info(f"使用API密钥: {api_key}")  # 可能泄露密钥
```

---

## 日志分析工具

### 1. 简单统计

```bash
# 统计今天的错误数量
grep -c "ERROR" logs/app_20260208.log

# 统计每个模块的日志数量
grep -o "src\.[^ ]*" logs/app_20260208.log | sort | uniq -c
```

### 2. 可视化工具

推荐使用以下工具分析日志：
- **Windows**: LogExpert, LogParser
- **Linux/Mac**: lnav, multitail
- **跨平台**: Graylog, ELK Stack (Elasticsearch + Logstash + Kibana)

---

## 更新日期

**最后更新**: 2026-02-08
**版本**: 1.0

---

**版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)**
