from typing import Optional
import os


def get_api_key_from_environment() -> Optional[str]:
    """
    Get the API key from the environment variable.
    """
    return os.getenv("BASEER_API_KEY", os.getenv("MISRAJ_API_KEY"))
