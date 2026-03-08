"""
API层 - 统一的API调用接口

这个模块提供了统一的API客户端，支持：
- 多提供商切换
- 自动重试和退避
- 响应缓存
- 速率限制
- 负载均衡

使用示例：
    from src.api import UnifiedAPIClient, create_api_client

    # 创建客户端
    client = create_api_client([
        {
            "provider_id": "openai",
            "api_key": "sk-...",
            "enabled": True
        }
    ])

    # 生成文本
    response = client.generate(
        messages=[
            {"role": "user", "content": "写一首诗"}
        ],
        temperature=0.8
    )

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

from .client import (
    UnifiedAPIClient,
    ResponseCache,
    RateLimiter,
    ProviderConnection,
    create_api_client,
    get_api_client
)

__all__ = [
    "UnifiedAPIClient",
    "ResponseCache",
    "RateLimiter",
    "ProviderConnection",
    "create_api_client",
    "get_api_client",
]
