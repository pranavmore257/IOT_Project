/*
 * ==============================================================================
 * PROJECT: Smart Acoustic & Vision Traffic Signal (ESP32 IoT Controller)
 * SUBTITLE: Real-Time Multimodal AI Traffic Signal Management
 * 
 * DESCRIPTION:
 * Controls miniature 4-way physical traffic signal LEDs (North, South, East, West)
 * based on commands received via MQTT from the Python AI Decision Engine.
 * 
 * FAIL-SAFE:
 * If Wi-Fi or MQTT connection is lost for > 15 seconds, the ESP32 automatically
 * falls back to an autonomous local cycle with safe yellow transitions.
 * ==============================================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==============================================================================
// 1. PIN DEFINITIONS (Easily Configurable for Breadboard Wiring)
// ==============================================================================
// NORTH INTERSECTION LEDs
#define PIN_NORTH_RED     23
#define PIN_NORTH_YELLOW  22
#define PIN_NORTH_GREEN   21

// SOUTH INTERSECTION LEDs
#define PIN_SOUTH_RED     19
#define PIN_SOUTH_YELLOW  18
#define PIN_SOUTH_GREEN   5

// EAST INTERSECTION LEDs
#define PIN_EAST_RED      17
#define PIN_EAST_YELLOW   16
#define PIN_EAST_GREEN    4

// WEST INTERSECTION LEDs
#define PIN_WEST_RED      0
#define PIN_WEST_YELLOW   2
#define PIN_WEST_GREEN    15

// OPTIONAL BUZZER (Beeps during Emergency Corridor)
#define PIN_BUZZER        13

// ==============================================================================
// 2. NETWORK & MQTT CONFIGURATION
// ==============================================================================
const char* WIFI_SSID       = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD   = "YOUR_WIFI_PASSWORD";

const char* MQTT_BROKER     = "192.168.1.100";  // IP address of Laptop running backend
const int   MQTT_PORT       = 1883;
const char* MQTT_CLIENT_ID  = "ESP32_Traffic_Signal";
const char* MQTT_USER       = "";               // Leave blank if no authentication
const char* MQTT_PASSWORD   = "";

// MQTT TOPICS
const char* TOPIC_SIGNAL    = "traffic/signal";
const char* TOPIC_STATUS    = "traffic/status";

// ==============================================================================
// 3. GLOBAL OBJECTS & STATE VARIABLES
// ==============================================================================
WiFiClient espClient;
PubSubClient mqttClient(espClient);

unsigned long lastMqttMessageTime = 0;
unsigned long lastHeartbeatTime   = 0;
const unsigned long FAILSAFE_TIMEOUT_MS = 15000;  // 15 seconds timeout
bool isAutonomousMode = false;

// ==============================================================================
// 4. HELPER FUNCTIONS: LED HARDWARE CONTROL
// ==============================================================================
void setupPins() {
  pinMode(PIN_NORTH_RED, OUTPUT);
  pinMode(PIN_NORTH_YELLOW, OUTPUT);
  pinMode(PIN_NORTH_GREEN, OUTPUT);

  pinMode(PIN_SOUTH_RED, OUTPUT);
  pinMode(PIN_SOUTH_YELLOW, OUTPUT);
  pinMode(PIN_SOUTH_GREEN, OUTPUT);

  pinMode(PIN_EAST_RED, OUTPUT);
  pinMode(PIN_EAST_YELLOW, OUTPUT);
  pinMode(PIN_EAST_GREEN, OUTPUT);

  pinMode(PIN_WEST_RED, OUTPUT);
  pinMode(PIN_WEST_YELLOW, OUTPUT);
  pinMode(PIN_WEST_GREEN, OUTPUT);

  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);

  // Turn all RED during boot
  setAllRed();
}

void setSignalHead(int pinRed, int pinYellow, int pinGreen, const char* state) {
  if (strcmp(state, "GREEN") == 0) {
    digitalWrite(pinRed, LOW);
    digitalWrite(pinYellow, LOW);
    digitalWrite(pinGreen, HIGH);
  } else if (strcmp(state, "YELLOW") == 0) {
    digitalWrite(pinRed, LOW);
    digitalWrite(pinYellow, HIGH);
    digitalWrite(pinGreen, LOW);
  } else { // Default RED
    digitalWrite(pinRed, HIGH);
    digitalWrite(pinYellow, LOW);
    digitalWrite(pinGreen, LOW);
  }
}

void setAllRed() {
  setSignalHead(PIN_NORTH_RED, PIN_NORTH_YELLOW, PIN_NORTH_GREEN, "RED");
  setSignalHead(PIN_SOUTH_RED, PIN_SOUTH_YELLOW, PIN_SOUTH_GREEN, "RED");
  setSignalHead(PIN_EAST_RED, PIN_EAST_YELLOW, PIN_EAST_GREEN, "RED");
  setSignalHead(PIN_WEST_RED, PIN_WEST_YELLOW, PIN_WEST_GREEN, "RED");
}

void applySignals(const char* north, const char* south, const char* east, const char* west, bool buzzerActive) {
  setSignalHead(PIN_NORTH_RED, PIN_NORTH_YELLOW, PIN_NORTH_GREEN, north);
  setSignalHead(PIN_SOUTH_RED, PIN_SOUTH_YELLOW, PIN_SOUTH_GREEN, south);
  setSignalHead(PIN_EAST_RED, PIN_EAST_YELLOW, PIN_EAST_GREEN, east);
  setSignalHead(PIN_WEST_RED, PIN_WEST_YELLOW, PIN_WEST_GREEN, west);
  digitalWrite(PIN_BUZZER, buzzerActive ? HIGH : LOW);
}

// ==============================================================================
// 5. MQTT MESSAGE CALLBACK & JSON PARSER
// ==============================================================================
void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  lastMqttMessageTime = millis();
  isAutonomousMode = false;

  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, payload, length);

  if (error) {
    Serial.print(F("JSON parsing failed: "));
    Serial.println(error.f_str());
    return;
  }

  const char* mode = doc["mode"] | "NORMAL";
  JsonObject signals = doc["signals"];

  const char* north = signals["NORTH"] | "RED";
  const char* south = signals["SOUTH"] | "RED";
  const char* east  = signals["EAST"]  | "RED";
  const char* west  = signals["WEST"]  | "RED";

  bool isEmergency = (strcmp(mode, "EMERGENCY") == 0);
  applySignals(north, south, east, west, isEmergency);

  Serial.printf("[SIGNAL UPDATE] Mode: %s | N:%s S:%s E:%s W:%s\n", mode, north, south, east, west);
}

// ==============================================================================
// 6. NETWORK & MQTT RECONNECTION
// ==============================================================================
void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi connected! IP Address: " + WiFi.localIP().toString());
  } else {
    Serial.println("\nWi-Fi connection failed! Running autonomous local cycle.");
  }
}

void connectMQTT() {
  if (mqttClient.connected()) return;

  Serial.print("Connecting to MQTT Broker at ");
  Serial.println(MQTT_BROKER);

  if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD)) {
    Serial.println("MQTT Connected successfully!");
    mqttClient.subscribe(TOPIC_SIGNAL);
    lastMqttMessageTime = millis();
  } else {
    Serial.print("MQTT connection failed, rc=");
    Serial.println(mqttClient.state());
  }
}

void sendHeartbeat() {
  if (!mqttClient.connected()) return;

  StaticJsonDocument<256> doc;
  doc["device"] = "ESP32_TRAFFIC_SIGNAL";
  doc["status"] = isAutonomousMode ? "AUTONOMOUS_FALLBACK" : "ONLINE_SLAVE";
  doc["ip"] = WiFi.localIP().toString();
  doc["rssi"] = WiFi.RSSI();
  doc["uptime_ms"] = millis();

  char buffer[256];
  serializeJson(doc, buffer);
  mqttClient.publish(TOPIC_STATUS, buffer);
}

// ==============================================================================
// 7. FAIL-SAFE AUTONOMOUS FALLBACK (Runs if Wi-Fi/MQTT is disconnected)
// ==============================================================================
void runAutonomousFailsafe() {
  isAutonomousMode = true;
  digitalWrite(PIN_BUZZER, LOW);

  // Phase 1: NS Green, EW Red (6s)
  applySignals("GREEN", "GREEN", "RED", "RED", false);
  delay(6000);

  // Phase 2: NS Yellow, EW Red (2s)
  applySignals("YELLOW", "YELLOW", "RED", "RED", false);
  delay(2000);

  // Phase 3: All Red (1s)
  applySignals("RED", "RED", "RED", "RED", false);
  delay(1000);

  // Phase 4: EW Green, NS Red (6s)
  applySignals("RED", "RED", "GREEN", "GREEN", false);
  delay(6000);

  // Phase 5: EW Yellow, NS Red (2s)
  applySignals("RED", "RED", "YELLOW", "YELLOW", false);
  delay(2000);

  // Phase 6: All Red (1s)
  applySignals("RED", "RED", "RED", "RED", false);
  delay(1000);
}

// ==============================================================================
// 8. MAIN SETUP & LOOP
// ==============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=============================================");
  Serial.println("  Smart Acoustic & Vision Traffic Signal");
  Serial.println("  ESP32 Miniature 4-Way Traffic Controller");
  Serial.println("=============================================");

  setupPins();

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(onMqttMessage);
  mqttClient.setBufferSize(512);

  connectWiFi();
  connectMQTT();
  lastMqttMessageTime = millis();
}

void loop() {
  // Check Wi-Fi and MQTT
  if (WiFi.status() == WL_CONNECTED) {
    if (!mqttClient.connected()) {
      connectMQTT();
    } else {
      mqttClient.loop();
    }
  }

  // Periodic heartbeat every 4 seconds
  if (millis() - lastHeartbeatTime > 4000) {
    sendHeartbeat();
    lastHeartbeatTime = millis();
  }

  // Check failsafe condition
  if (millis() - lastMqttMessageTime > FAILSAFE_TIMEOUT_MS) {
    Serial.println("[WARNING] No message from AI Backend for > 15s. Running autonomous failsafe...");
    runAutonomousFailsafe();
    lastMqttMessageTime = millis(); // Refresh after cycle
  }

  delay(20);
}
