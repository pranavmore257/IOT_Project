import os
from pathlib import Path
from typing import Any, Dict
import yaml

CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"

def load_config() -> Dict[str, Any]:
    """Loads configuration from YAML with environment variable overrides."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # Environment variable overrides
    if "CAMERA_INDEX" in os.environ:
        try:
            cfg["video"]["camera_index"] = int(os.environ["CAMERA_INDEX"])
        except ValueError:
            pass

    if "MQTT_BROKER" in os.environ:
        cfg["mqtt"]["broker"] = os.environ["MQTT_BROKER"]
    if "MQTT_PORT" in os.environ:
        try:
            cfg["mqtt"]["port"] = int(os.environ["MQTT_PORT"])
        except ValueError:
            pass
    if "MQTT_USERNAME" in os.environ:
        cfg["mqtt"]["username"] = os.environ["MQTT_USERNAME"]
    if "MQTT_PASSWORD" in os.environ:
        cfg["mqtt"]["password"] = os.environ["MQTT_PASSWORD"]

    if "DATABASE_PATH" in os.environ:
        cfg["database"]["db_path"] = os.environ["DATABASE_PATH"]

    return cfg

# Global config singleton
CONFIG = load_config()
