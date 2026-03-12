import os
import json
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
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Mapping of environment variables to config keys
    # Example: OPENAI_API_KEY -> providers['openai']['api_key']
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
    
    if "providers" not in config:
        config["providers"] = {}
    
    updated = False
    for env_var, (provider, key) in mapping.items():
        value = os.environ.get(env_var)
        if value:
            if provider not in config["providers"]:
                config["providers"][provider] = {}
            config["providers"][provider][key] = value
            updated = True
            
    if updated:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"Updated configuration with secrets from environment variables.")
    
    return config
