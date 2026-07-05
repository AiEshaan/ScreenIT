import os
from pathlib import Path
from dotenv import load_dotenv, set_key

# Find the workspace root where .env is located (assumes backend/app/core/config.py)
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = WORKSPACE_ROOT / ".env"

# Ensure .env exists
if not ENV_PATH.exists():
    ENV_PATH.touch()

# Load env immediately on import
load_dotenv(ENV_PATH)

class SettingsManager:
    @staticmethod
    def get_provider_key(provider: str) -> str:
        """Get the API key for a provider."""
        # Convert provider name to env key (e.g. 'openai' -> 'OPENAI_API_KEY')
        key_name = f"{provider.upper()}_API_KEY"
        return os.environ.get(key_name, "")

    @staticmethod
    def set_provider_key(provider: str, key: str) -> None:
        """Save an API key to the .env file and update the environment."""
        key_name = f"{provider.upper()}_API_KEY"
        # Update .env
        set_key(dotenv_path=str(ENV_PATH), key_to_set=key_name, value_to_set=key)
        # Update current process environment
        os.environ[key_name] = key

    @staticmethod
    def get_all_providers_status() -> dict:
        """Check which providers have keys configured."""
        return {
            "openai": "configured" if SettingsManager.get_provider_key("openai") else "missing",
            "openrouter": "configured" if SettingsManager.get_provider_key("openrouter") else "missing",
            "anthropic": "configured" if SettingsManager.get_provider_key("anthropic") else "missing",
            "gemini": "configured" if SettingsManager.get_provider_key("gemini") else "missing",
        }
