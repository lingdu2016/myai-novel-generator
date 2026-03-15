import json
import os
from pathlib import Path

from src.config.paths import get_config_dir


def load_secrets_to_config():
    """
    Read API keys from Hugging Face Secrets (environment variables)
    and update/create the user_config.json file.
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "user_config.json"

    config = {}
    if config_file.exists():
        try:
            with open(config_file, encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")

    # Handle backward compatibility: convert old dict format to list format
    if "providers" in config and isinstance(config["providers"], dict):
        print("Converting old dict format to list format...")
        old_providers = config["providers"]
        config["providers"] = []

        # Map old provider keys to their provider_id
        provider_key_map = {
            "google": "google",
            "openai": "openai",
            "anthropic": "anthropic",
            "deepseek": "deepseek",
            "mistral": "mistral",
            "groq": "groq",
            "together": "together",
            "openrouter": "openrouter",
            "aliyun": "alibaba",
            "zhipu": "zhipu",
            "moonshot": "moonshot",
            "baichuan": "baichuan",
            "minimax": "minimax",
        }

        for provider_key, provider_data in old_providers.items():
            provider_id = provider_key_map.get(provider_key, provider_key)
            config["providers"].append({
                "name": provider_key,
                "provider_id": provider_id,
                "api_key": provider_data.get("api_key", ""),
                "enabled": True
            })
        print(f"Converted {len(config['providers'])} providers to new format")

    # Initialize providers as list if not present
    if "providers" not in config:
        config["providers"] = []

    # Mapping of environment variables to config keys
    # Example: OPENAI_API_KEY -> providers[...]['api_key']
    mapping = {
        "OPENAI_API_KEY": ("openai", "api_key"),
        "CLAUDE_API_KEY": ("anthropic", "api_key"),
        "ANTHROPIC_API_KEY": ("anthropic", "api_key"),
        "GEMINI_API_KEY": ("google", "api_key"),
        "DEEPSEEK_API_KEY": ("deepseek", "api_key"),
        "MISTRAL_API_KEY": ("mistral", "api_key"),
        "GROQ_API_KEY": ("groq", "api_key"),
        "TOGETHER_API_KEY": ("together", "api_key"),
        "OPENROUTER_API_KEY": ("openrouter", "api_key"),
        "QWEN_API_KEY": ("aliyun", "api_key"),
        "DASHSCOPE_API_KEY": ("aliyun", "api_key"),
        "ZHIPU_API_KEY": ("zhipu", "api_key"),
        "MOONSHOT_API_KEY": ("moonshot", "api_key"),
        "BAICHUAN_API_KEY": ("baichuan", "api_key"),
        "MINIMAX_API_KEY": ("minimax", "api_key"),
    }

    updated = False
    for env_var, (provider, key) in mapping.items():
        value = os.environ.get(env_var)
        if value:
            # Find if provider already exists in list
            existing = None
            for p in config["providers"]:
                if p.get("provider_id") == provider or p.get("name") == provider:
                    existing = p
                    break

            if existing:
                existing[key] = value
            else:
                # Get provider config for additional settings
                from src.config.providers import ProviderFactory
                preset_config = ProviderFactory.get_provider_config(provider)

                provider_entry = {
                    "name": provider,
                    "provider_id": provider,
                    key: value,
                    "enabled": True
                }

                # Add default values from preset config
                if preset_config:
                    provider_entry["model"] = preset_config.default_model
                    provider_entry["base_url"] = preset_config.base_url
                    provider_entry["timeout"] = 60
                    provider_entry["max_retries"] = 3

                config["providers"].append(provider_entry)

            updated = True

    if updated:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("Updated configuration with secrets from environment variables.")

    return config
