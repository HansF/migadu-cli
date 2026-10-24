"""CLI configuration loader — reads from env or CLI flags."""
import os

def load_config(email=None, api_key=None, domain=None):
    return {
        "email": email or os.getenv("MIGADU_EMAIL"),
        "api_key": api_key or os.getenv("MIGADU_API_KEY"),
        "default_domain": domain or os.getenv("MIGADU_DOMAIN"),
    }