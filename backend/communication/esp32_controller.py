import time
from typing import Dict, Any, Optional
from backend.config.settings import CONFIG
from backend.communication.mqtt_client import MQTTTrafficClient

class ESP32Controller:
    """Manages ESP32 communication and simulation mode fallbacks."""

    def __init__(self, mqtt_client: MQTTTrafficClient):
        self.mqtt_client = mqtt_client
        esp_cfg = CONFIG.get("esp32", {})
        self.heartbeat_timeout = esp_cfg.get("heartbeat_timeout_sec", 10.0)
        self.pins = esp_cfg.get("pins", {})

        self.last_heartbeat = 0.0
        self.esp32_status_data = {}
        self.mqtt_client.add_status_callback(self._on_esp32_status)

    def _on_esp32_status(self, data: Dict[str, Any]):
        self.last_heartbeat = time.time()
        self.esp32_status_data = data

    def dispatch_signal_state(self, signal_info: Dict[str, Any], mode: str, priority: str):
        """Sends command to ESP32 over MQTT."""
        payload = {
            "mode": mode,
            "priority": priority,
            "state": signal_info.get("state"),
            "remaining": signal_info.get("remaining_seconds"),
            "duration": signal_info.get("allocated_seconds"),
            "signals": signal_info.get("signals"),
            "emergency_target": signal_info.get("emergency_target"),
            "timestamp": time.time()
        }
        self.mqtt_client.publish_signal(payload)

    def get_status(self) -> Dict[str, Any]:
        now = time.time()
        is_esp_active = (now - self.last_heartbeat) < self.heartbeat_timeout if self.last_heartbeat > 0 else False
        mqtt_status = self.mqtt_client.get_status()

        return {
            "esp32_connected": is_esp_active,
            "control_mode": "HARDWARE (ESP32)" if is_esp_active else "SIMULATION MODE",
            "mqtt_connected": mqtt_status["connected"],
            "broker": mqtt_status["broker"],
            "port": mqtt_status["port"],
            "last_heartbeat_ago_sec": round(now - self.last_heartbeat, 1) if self.last_heartbeat > 0 else None,
            "pin_configuration": self.pins
        }
