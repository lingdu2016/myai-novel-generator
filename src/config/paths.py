import os
from pathlib import Path

def get_data_dir():
    """
    Returns the root data directory.
    On Hugging Face Spaces, this is /data.
    Locally, it's the project root.
    """
    # Use HF_SPACE environment variable to detect if we are running on HF Spaces
    if os.environ.get("HF_SPACE") or os.environ.get("USE_DATA_DIR"):
        return Path("/data")
    return Path(".")

def get_projects_dir():
    return get_data_dir() / "projects"

def get_logs_dir():
    return get_data_dir() / "logs"

def get_cache_dir():
    return get_data_dir() / "cache"

def get_exports_dir():
    return get_data_dir() / "exports"

def get_config_dir():
    # If we are in HF Space, config should also be in /data to persist user settings
    return get_data_dir() / "config"

def ensure_dirs():
    """Ensure all required directories exist."""
    get_projects_dir().mkdir(parents=True, exist_ok=True)
    get_logs_dir().mkdir(parents=True, exist_ok=True)
    get_cache_dir().mkdir(parents=True, exist_ok=True)
    get_exports_dir().mkdir(parents=True, exist_ok=True)
    get_config_dir().mkdir(parents=True, exist_ok=True)
    
    # Subdirectories
    (get_cache_dir() / "coherence").mkdir(parents=True, exist_ok=True)
    (get_cache_dir() / "api").mkdir(parents=True, exist_ok=True)
    (get_cache_dir() / "generation").mkdir(parents=True, exist_ok=True)
    (get_cache_dir() / "summaries").mkdir(parents=True, exist_ok=True)
    (get_logs_dir() / "api_samples").mkdir(parents=True, exist_ok=True)
