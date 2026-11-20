import time
from typing import Dict, Any, Optional
from backend.config.settings import CONFIG
from backend.communication.mqtt_client import MQTTTrafficClient

class ESP8266Controller:
    """Manages ESP8266 communication and simulation mode fallbacks."""

    def __init__(self, mqtt_client: MQTTTrafficClient):
        self.mqtt_client = mqtt_client
        hardware_cfg = CONFIG.get("esp8266", {})
        self.heartbeat_timeout = hardware_cfg.get("heartbeat_timeout_sec", 10.0)
        self.pin_configuration = hardware_cfg.get("shift_register", {})

        self.last_heartbeat = 0.0
        self.hardware_status_data = {}
        self.mqtt_client.add_status_callback(self._on_hardware_status)

    def _on_hardware_status(self, data: Dict[str, Any]):
        self.last_heartbeat = time.time()
        self.hardware_status_data = data

    def dispatch_signal_state(self, signal_info: Dict[str, Any], mode: str, priority: str):
        """Sends the current signal command to the ESP8266 over MQTT."""
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
        is_hardware_active = (
            now - self.last_heartbeat < self.heartbeat_timeout
            if self.last_heartbeat > 0
            else False
        )
        mqtt_status = self.mqtt_client.get_status()

        return {
            "hardware_connected": is_hardware_active,
            "control_mode": "HARDWARE (ESP8266)" if is_hardware_active else "SIMULATION MODE",
            "mqtt_connected": mqtt_status["connected"],
            "broker": mqtt_status["broker"],
            "port": mqtt_status["port"],
            "last_heartbeat_ago_sec": round(now - self.last_heartbeat, 1) if self.last_heartbeat > 0 else None,
            "pin_configuration": self.pin_configuration,
            "device": self.hardware_status_data.get("device")
        }
