"""
API采样日志记录器

记录API请求/响应的样本，用于调试和监控。
采用采样策略，避免日志过多。

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

import logging
import random
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class APILogger:
    """
    API采样日志记录器

    策略：
    - 开头阶段：前N条必记录
    - 中间阶段：随机采样
    - 结尾阶段：最后几条必记录
    """

    # 全局单例
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        sample_rate: float = 0.05,
        min_samples: int = 3,
        max_samples: int = 15,
        tail_samples: int = 3
    ):
        """
        初始化采样日志记录器

        Args:
            sample_rate: 中间阶段随机采样概率 (0-1)
            min_samples: 开头必记录样本数
            max_samples: 最大记录样本数（不含结尾）
            tail_samples: 结尾必记录样本数
        """
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return

        self.sample_rate = sample_rate
        self.min_samples = min_samples
        self.max_samples = max_samples
        self.tail_samples = tail_samples
        self.logged_count = 0
        self.total_requests = 0
        self.session_start = datetime.now()

        # 日志目录
        self.log_dir = Path("logs/api_samples")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 当前会话日志文件
        self.log_file = self.log_dir / f"api_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

        # 是否启用
        self.enabled = True

        self._initialized = True
        logger.info(f"API采样日志初始化: 文件={self.log_file}, 采样率={sample_rate}")

    def should_log(self) -> bool:
        """判断是否应该记录此次请求"""
        if not self.enabled:
            return False

        self.total_requests += 1

        # 开头阶段: 前 min_samples 次必记录
        if self.logged_count < self.min_samples:
            return True

        # 中间阶段: 随机采样，但有上限
        if self.logged_count < self.max_samples:
            return random.random() < self.sample_rate

        # 超过最大样本数后，不再记录（除非总请求量很大，记录结尾）
        if self.total_requests > 50 and self.logged_count < self.max_samples + self.tail_samples:
            # 记录结尾样本
            return random.random() < 0.3

        return False

    def log_exchange(
        self,
        endpoint: str,
        request_data: Dict[str, Any],
        response_data: Optional[str] = None,
        duration_ms: Optional[float] = None,
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        记录完整的请求-响应交换

        Args:
            endpoint: API端点描述
            request_data: 请求数据
            response_data: 响应数据
            duration_ms: 请求耗时（毫秒）
            error: 错误信息（如果有）
            metadata: 额外元数据
        """
        if not self.should_log():
            return

        self.logged_count += 1

        # 确定阶段
        if self.logged_count <= self.min_samples:
            phase = "开头"
        elif self.logged_count <= self.max_samples:
            phase = "中间"
        else:
            phase = "结尾"

        # 脱敏处理
        sanitized_request = self._sanitize(request_data)
        sanitized_response = self._sanitize_response(response_data) if response_data else None

        log_entry = {
            "phase": phase,
            "request_id": self.logged_count,
            "total_requests": self.total_requests,
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "duration_ms": duration_ms,
            "request": sanitized_request,
            "response": sanitized_response,
            "error": str(error) if error else None,
            "metadata": metadata or {}
        }

        # 记录到普通日志
        logger.info(f"[API采样-{phase}] #{self.logged_count}/{self.total_requests} - {endpoint}")

        # 写入采样日志文件
        self._write_to_file(log_entry)

    def _sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理请求数据中的敏感信息"""
        if not isinstance(data, dict):
            return data

        cleaned = {}
        for k, v in data.items():
            # 脱敏API Key
            if 'api_key' in k.lower() or 'key' in k.lower():
                if isinstance(v, str) and len(v) > 10:
                    cleaned[k] = v[:8] + "***" + v[-4:]
                else:
                    cleaned[k] = "***REDACTED***"
            # 截断过长的内容
            elif isinstance(v, str) and len(v) > 2000:
                cleaned[k] = v[:1000] + "...(truncated, original length: " + str(len(v)) + ")"
            elif isinstance(v, list) and 'message' in k.lower():
                # 处理消息列表
                cleaned[k] = self._sanitize_messages(v)
            else:
                cleaned[k] = v
        return cleaned

    def _sanitize_messages(self, messages: list) -> list:
        """清理消息内容"""
        if not isinstance(messages, list):
            return messages

        cleaned = []
        for msg in messages:
            if isinstance(msg, dict):
                cleaned_msg = {}
                for k, v in msg.items():
                    if k == 'content' and isinstance(v, str) and len(v) > 1000:
                        # 保留内容的前500和后200字符
                        cleaned_msg[k] = v[:500] + "\n...(tripped " + str(len(v) - 700) + " chars)...\n" + v[-200:]
                    else:
                        cleaned_msg[k] = v
                cleaned.append(cleaned_msg)
            else:
                cleaned.append(msg)
        return cleaned

    def _sanitize_response(self, response: str) -> str:
        """清理响应数据"""
        if not isinstance(response, str):
            return str(response)

        if len(response) > 3000:
            return response[:1500] + "\n...(tripped " + str(len(response) - 2500) + " chars)...\n" + response[-1000:]
        return response

    def _write_to_file(self, log_entry: Dict[str, Any]) -> None:
        """写入日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"写入采样日志失败: {e}")

    def summary(self) -> str:
        """生成运行摘要"""
        duration = (datetime.now() - self.session_start).total_seconds()

        summary = f"""
【API采样日志摘要】
运行时长: {duration:.1f}秒
总请求数: {self.total_requests}
记录样本数: {self.logged_count}
实际采样率: {self.logged_count/self.total_requests*100:.1f}% (if {self.total_requests} > 0 else 0)
日志文件: {self.log_file}
"""
        logger.info(summary)
        return summary

    def reset(self) -> None:
        """重置计数器（用于新会话）"""
        self.logged_count = 0
        self.total_requests = 0
        self.session_start = datetime.now()
        self.log_file = self.log_dir / f"api_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        logger.info("API采样日志计数器已重置")

    def set_enabled(self, enabled: bool) -> None:
        """启用/禁用采样日志"""
        self.enabled = enabled
        logger.info(f"API采样日志{'启用' if enabled else '禁用'}")


# 全局实例
api_logger = APILogger()


def get_api_logger() -> APILogger:
    """获取全局API日志记录器"""
    return api_logger
