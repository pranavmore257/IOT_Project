import json
import time
import threading
from typing import Dict, Any, Callable, Optional

class MQTTTrafficClient:
    """MQTT communication client for publishing traffic signals and listening to ESP32."""

    def __init__(self, mqtt_config: Dict[str, Any]):
        self.config = mqtt_config
        self.broker = mqtt_config.get("broker", "localhost")
        self.port = mqtt_config.get("port", 1883)
        self.client_id = mqtt_config.get("client_id", "traffic_signal_ai_backend")
        self.username = mqtt_config.get("username", "")
        self.password = mqtt_config.get("password", "")
        self.topics = mqtt_config.get("topics", {})

        self.client = None
        self.is_connected = False
        self.status_callbacks = []
        self.last_heartbeat_time = 0.0
        self.lock = threading.Lock()

        self._init_client()

    def _init_client(self):
        try:
            import paho.mqtt.client as mqtt
            # Support both Paho-MQTT v2 and v1
            if hasattr(mqtt, "CallbackAPIVersion"):
                try:
                    self.client = mqtt.Client(
                        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                        client_id=self.client_id
                    )
                except Exception:
                    self.client = mqtt.Client(
                        callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
                        client_id=self.client_id
                    )
            else:
                self.client = mqtt.Client(client_id=self.client_id)

            if self.username:
                self.client.username_pw_set(self.username, self.password)

            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
        except Exception as e:
            print(f"[MQTTTrafficClient] MQTT init warning: {e}")
            self.client = None

    def start(self):
        if not self.client:
            return
        try:
            # Non-blocking connection attempt
            self.client.connect_async(self.broker, self.port, keepalive=self.config.get("keepalive", 60))
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTTTrafficClient] Could not connect to MQTT broker {self.broker}:{self.port} ({e}). Simulation mode active.")
            self.is_connected = False

    def stop(self):
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
            self.is_connected = False

    def _on_connect(self, client, userdata, *args):
        # Compatible with both v1 (client, userdata, flags, rc) and v2 (client, userdata, flags, reason_code, properties)
        rc = args[1] if len(args) >= 2 and isinstance(args[1], int) else (args[0] if len(args) >= 1 and isinstance(args[0], int) else 0)
        # In v2 rc is reason_code
        if rc == 0 or getattr(rc, "is_failure", False) is False:
            self.is_connected = True
            status_topic = self.topics.get("status", "traffic/status")
            client.subscribe(status_topic)
            print(f"[MQTTTrafficClient] Connected to MQTT broker at {self.broker}:{self.port}")
        else:
            self.is_connected = False

    def _on_disconnect(self, client, userdata, *args):
        self.is_connected = False

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            self.last_heartbeat_time = time.time()
            for cb in self.status_callbacks:
                cb(payload)
        except Exception:
            pass

    def add_status_callback(self, callback: Callable[[Dict[str, Any]], None]):
        self.status_callbacks.append(callback)

    def publish_signal(self, payload: Dict[str, Any]):
        if not self.is_connected or not self.client:
            return
        try:
            topic = self.topics.get("signal", "traffic/signal")
            self.client.publish(topic, json.dumps(payload), qos=1)
        except Exception as e:
            print(f"[MQTTTrafficClient] Publish signal error: {e}")

    def publish_decision(self, payload: Dict[str, Any]):
        if not self.is_connected or not self.client:
            return
        try:
            topic = self.topics.get("decision", "traffic/decision")
            self.client.publish(topic, json.dumps(payload), qos=0)
        except Exception as e:
            print(f"[MQTTTrafficClient] Publish decision error: {e}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "broker": self.broker,
            "port": self.port,
            "connected": self.is_connected,
            "last_heartbeat_time": self.last_heartbeat_time
        }
