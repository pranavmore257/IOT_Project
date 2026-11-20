# Smart Acoustic & Vision Traffic Signal

> **Real-Time Multimodal AI Traffic Signal Management using Laptop Audio/Video and an ESP8266 IoT Prototype**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/Vision%20AI-Ultralytics%20YOLOv8n-FF6F00.svg)](https://docs.ultralytics.com/)
[![Audio AI](https://img.shields.io/badge/Audio%20AI-MFCC%20%2B%20Random%20Forest%20(96.7%25)-green.svg)]()
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite%20%2B%20Tailwind-61DAFB.svg)](https://vitejs.dev/)
[![ESP8266](https://img.shields.io/badge/IoT%20Hardware-ESP8266%20%2B%2074HC595-E7352C.svg)](https://www.espressif.com/)

---

## 1. Project Overview

The **Smart Acoustic & Vision Traffic Signal** is an educational AI + IoT prototype. The laptop webcam and microphone provide live sensor input; the decision engine sends signal commands over Wi-Fi/MQTT to an ESP8266 NodeMCU, which drives tabletop LEDs through two cascaded 74HC595 shift registers.

> [!NOTE]
> **Prototype Scope:** This is an academic tabletop prototype, not a certified traffic controller and must never be connected to public-road signals. Camera position and the configured image ROIs affect lane counts.

### The Problem It Solves
Traditional fixed-timer traffic lights waste hours in traffic congestion and delay emergency vehicles (ambulances, fire engines, police), leading to preventable fatalities. This system solves both issues simultaneously:
1. **Dynamic Congestion Relief:** Camera detects traffic volume and automatically extends green light durations for congested approaches.
2. **Emergency Green Corridors:** Fuses audio siren classification with visual vehicle recognition to clear safe green paths for emergency vehicles.

---

## 2. System Architecture

```text
                     +-----------------------------------+
                     |         LAPTOP SENSORS            |
                     +-----------------+-----------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
         [ Laptop Webcam ]                       [ Laptop Microphone ]
                   |                                       |
                   v                                       v
         [ OpenCV Capture ]                     [ 16kHz Audio Stream ]
                   |                                       |
                   v                                       v
         [ Ultralytics YOLOv8 ]                 [ MFCC / Mel-Spectrogram ]
                   |                                       |
                   v                                       v
      [ Vehicle Counts + Density + ROI ]       [ Audio Event Classifier ]
      (Cars, Bikes, Buses, Trucks, Amb)        (Ambulance, Fire, Horn, Crash)
                   |                                       |
                   +-------------------+-------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |     MULTIMODAL DECISION ENGINE    |
                     |  Score = (0.50 * A) + (0.50 * V)  |
                     +-----------------+-----------------+
                                       |
                        +--------------+--------------+
                        |                             |
                        v                             v
             [ Routine / Congestion ]      [ Confirmed Emergency ]
                        |                             |
                        v                             v
             [ Adaptive Green Time ]       [ Emergency Green Corridor ]
                        |                             |
                        +--------------+--------------+
                                       |
                                       v
                     +-----------------------------------+
                     |      MQTT Broker (1883) / Wi-Fi   |
                     |         topic: traffic/signal     |
                     +-----------------+-----------------+
                                       |
                                       v
                     +-----------------------------------+
                     |    ESP8266 + 2 x 74HC595          |
                     |   (Fail-Safe Autonomous Watchdog) |
                     +-----------------+-----------------+
                                       |
                                       v
                     +-----------------------------------+
                     |   Miniature 4-Way Traffic Signal  |
                     |      12 Physical LEDs (R/Y/G)     |
                     +-----------------------------------+
```

---

## 3. Multimodal Decision Rules

The decision engine evaluates acoustic and visual inputs using mathematical confidence fusion:

$$\text{EmergencyScore} = (W_{\text{audio}} \times C_{\text{audio}}) + (W_{\text{video}} \times C_{\text{video}})$$

* $W_{\text{audio}} = 0.50$, $W_{\text{video}} = 0.50$, Threshold $= 0.75$ (75%)

| Case | Audio AI | Video AI | System Decision | Traffic Action |
| :--- | :--- | :--- | :--- | :--- |
| **Case 1 (Dual AI)** | Ambulance Siren $\ge 60\%$ | Ambulance Detected $\ge 60\%$ | **EMERGENCY (High)** | **Green Corridor** on approaching direction |
| **Case 2 (Audio Only)** | Siren Detected $\ge 60\%$ | No visual vehicle | **POSSIBLE EMERGENCY** | 3.0s visual confirmation window (avoids false alarms) |
| **Case 3 (Video Only)** | Normal traffic sound | Ambulance Detected $\ge 80\%$ | **LOWER PRIORITY** | Visual priority green with silent siren handling |
| **Case 4 (Crash Sound)**| Accident / Impact $\ge 70\%$ | Any | **ACCIDENT ALERT** | Immediate all-RED safety hold |
| **Case 5 (Heavy Traffic)**| Heavy Honking / Normal | Vehicle Count $\ge 11$ | **ADAPTIVE CONGESTION** | Extends green light from 10s to 20s |

---

## 4. Hardware Requirements & Wiring

### Required Hardware
* **1x ESP8266 NodeMCU**
* **2x 74HC595 shift registers** for the complete 12-LED model
* **4x Red LEDs, 4x Yellow LEDs, 4x Green LEDs** (12 LEDs total for 4 directions)
* **12x 220Ω Resistors**
* **1x Breadboard & Jumper Wires**
* **1x USB Cable**
* **1x Laptop Webcam & Microphone**

### Stage 1: test one signal directly

Before adding the shift registers, use one LED of each color and three 220Ω resistors. Connect NodeMCU **D1 → resistor → red LED anode**, **D2 → resistor → yellow LED anode**, and **D5 → resistor → green LED anode**. Connect all three LED cathodes (short legs) to NodeMCU GND. Flash [`esp8266/stage1_test/stage1_test.ino`](./esp8266/stage1_test/stage1_test.ino); the cycle is red 3s, yellow 1s, green 3s. Do not connect the microphone/webcam to the ESP8266.

### Full four-way model: two cascaded shift registers

For the full model, remove the direct D1/D2/D5 LED connections and use one 220Ω resistor in series with each of the 12 LEDs. Power both 74HC595s from **3.3V**, join all grounds, tie **OE to GND** and **MR to 3.3V**, and connect the first register's Q7' to the second register's DS. Connect NodeMCU **D7 → DS (data)**, **D5 → SH_CP (clock)**, and **D6 → ST_CP (latch)**. Each LED output goes from its Q output through its own resistor to the LED anode; all cathodes go to GND.

| Register output | LED |
| :--- | :--- |
| First 74HC595 Q0-Q2 | North Red, Yellow, Green |
| First 74HC595 Q3-Q5 | South Red, Yellow, Green |
| First 74HC595 Q6-Q7, second Q0 | East Red, Yellow, Green |
| Second 74HC595 Q1-Q3 | West Red, Yellow, Green |

Use the full wiring table and board notes in [`esp8266/traffic_signal/traffic_signal.ino`](./esp8266/traffic_signal/traffic_signal.ino). The NodeMCU and both shift registers must share a common ground.

The controller phases the opposing approaches together (N/S, then E/W). It assigns each axis a separate green duration from its detected demand, bounded by the configured minimum and maximum. The lower-demand axis still receives its turn every cycle; this version does not grant independent right-of-way to each of the four approaches.

---

## 5. Software Installation & Setup

### Prerequisites
* **Python 3.10+**
* **Node.js 18+** & **npm**

### Step 1: Install Backend Dependencies
```bash
# Clone or open the repository
cd ProjectIoT

# Install Python requirements
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 6. Running the Application

### Option A: Run Backend Server
```bash
# From the project root
python -m backend.main
```
* Backend API will start at: `http://localhost:8000`
* Interactive API Docs (Swagger): `http://localhost:8000/docs`

### Option B: Run Frontend Dashboard
In a second terminal window:
```bash
cd frontend
npm run dev
```
* Open your browser at: `http://localhost:5173`

---

## 7. AI Model Training & Evaluation

The repository includes a complete offline training and evaluation pipeline for the custom audio classifier.

### Step 1: Generate Synthetic Acoustic Samples
Generates 120 samples across sirens, honking, accidents, and traffic:
```bash
python scripts/prepare_audio_dataset.py
```

### Step 2: Train Audio Classifier
Extracts 20-MFCC features and trains a Random Forest classifier:
```bash
python scripts/train_audio_model.py
```
* Generates `models/audio/audio_classifier.pkl`
* Exports evaluation metrics to `models/audio/metrics.json`
* **Test Accuracy: 96.67% | F1 Score: 96.63%**

### Step 3: View Model Evaluation Report
```bash
python scripts/evaluate_audio_model.py
```

---

## 8. College Demonstration Sequence (12-Step Walkthrough)

Follow this sequence during your project presentation or viva examination:

1. **Start System:** Start backend and frontend. The dashboard connects via WebSocket at 10 Hz.
2. **Observe System Status:** Check the top status bar for the laptop webcam/microphone and whether signal output is in ESP8266 hardware or simulation mode.
3. **Inspect 4-Way Traffic Cycle:** Watch the 4-way intersection rotate through North/South GREEN (10s) $\rightarrow$ YELLOW (3s) $\rightarrow$ ALL-RED (1s) $\rightarrow$ East/West GREEN.
4. **Demonstrate Video AI (YOLOv8):** Show cars, bikes, buses, and trucks on webcam. Bounding boxes, labels, confidences, and counts are drawn in real-time.
5. **Demonstrate Traffic Density & Adaptive Timing:** Click `[ Heavy Traffic ]` in Demo Controls or show multiple vehicles. Notice vehicle count jump to 14, density turn **HIGH**, and green duration extend to **20 seconds**.
6. **Demonstrate Audio AI:** Make sound or play a siren. Watch the live 32-band spectrogram jump, RMS activity bar rise, and classified sound change.
7. **Demonstrate Case 2 (False Alarm Suppression):** Click `[ Audio Siren Only ]`. Siren confidence is high, but without visual confirmation, the decision engine holds in **POSSIBLE EMERGENCY** without disrupting traffic.
8. **⭐ THE MAIN DEMONSTRATION (Case 1 Dual AI):**
   * Click `[ 🚑 Ambulance (Dual AI) ]` (or play an ambulance siren while showing an ambulance picture to webcam).
   * **Audio AI:** Ambulance Siren (95%).
   * **Video AI:** Ambulance Detected (92%) from NORTH.
   * **Multimodal Fusion:** Emergency Score $= 93.5\% \ge 75\%$.
   * **Decision:** `🚨 EMERGENCY: GREEN CORRIDOR (NORTH)`.
   * **ESP8266:** Conflicting East/West receives safe yellow clearance before North/South turns solid GREEN!
9. **Demonstrate Case 4 (Accident Safety Hold):** Click `[ Accident Sound ]`. Crash audio signature triggers immediate **ACCIDENT ALERT** and safe all-RED hold.
10. **Clear & Reset:** Click `[ Reset to Live ]`. The system cycles through yellow clearance and safely resumes normal routine 4-way traffic.
11. **View SQLite Event History:** Scroll down to the SQLite table to show all logged decisions, scores, and timestamps.
12. **Open Viva Specs Modal:** Click `[ AI Models & Viva Specs ]` in the top header to explain model architecture and formulas to the examiner.

---

## 9. ESP8266 Firmware & Live Hardware Setup

1. Install the Arduino IDE and add the ESP8266 board package using the official Boards Manager URL: `https://arduino.esp8266.com/stable/package_esp8266com_index.json`.
2. For the first bench test, open `esp8266/stage1_test/stage1_test.ino`, select **NodeMCU 1.0 (ESP-12E Module)** and the correct serial port, then upload and verify the 3s/1s/3s cycle.
3. Build the full four-way circuit with two 74HC595 shift registers, then open `esp8266/traffic_signal/traffic_signal.ino`. Install these Arduino Library Manager libraries:
   * `ArduinoJson` (v6 or v7)
   * `PubSubClient` (by Nick O'Leary)
4. Ensure an MQTT broker (for example Mosquitto) is reachable on the same Wi-Fi as the NodeMCU. Set the Wi-Fi credentials and laptop's LAN IPv4 address in the sketch:
   ```cpp
   const char* WIFI_SSID = "YOUR_WIFI_SSID";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* MQTT_BROKER = "192.168.1.100"; // Laptop IP running the MQTT broker
   ```
5. In `backend/config/config.yaml`, keep MQTT broker `localhost` when running the backend and broker directly on the laptop. Select **NodeMCU 1.0 (ESP-12E Module)**, upload the full sketch, and open Serial Monitor at `115200` baud.
6. Configure camera placement and `video.roi` in `backend/config/config.yaml` for the four approaches as seen by your webcam. Run the backend on the laptop; it uses camera index `0` and the default microphone unless overridden. Check `/api/status` and the dashboard: absent sensors or hardware are explicitly reported as simulation/disconnected, not live.

Backend configuration supports `CAMERA_INDEX`, `MQTT_BROKER`, `MQTT_PORT`, `MQTT_USERNAME`, and `MQTT_PASSWORD` environment overrides.

---

## 10. Automated Tests

Run the test suite using pytest:
```bash
python -m pytest tests/ -v
```
All 7 unit tests pass:
* `test_high_traffic_extends_green` (Verifies congestion adds green time)
* `test_density_thresholds` (Verifies LOW, MEDIUM, HIGH thresholds)
* `test_audio_video_emergency` (Verifies Case 1 dual confirmation triggers corridor)
* `test_audio_only_does_not_immediately_trigger` (Verifies false alarm prevention)
* `test_accident_impact_detection` (Verifies Case 4 crash acoustic hold)
* `test_signal_transition_is_safe` (Verifies green never switches without yellow)
* `test_emergency_preemption_safety` (Verifies safe yellow preemption)

---

## 11. Viva Examination Q&A Cheat-Sheet

| Question | Answer Summary |
| :--- | :--- |
| **Why not use real city traffic lights?** | Safety regulations and legal standards forbid uncertified prototypes from directly interfacing with municipal municipal grids. This prototype controls an accurate miniature 12-LED 4-way intersection. |
| **Why combine Audio and Video AI?** | Video alone cannot detect an emergency vehicle approaching around a blind corner or through heavy fog. Audio alone can be fooled by movies or phone ringtones. Fusing both yields high accuracy (>93%) and eliminates false preemption. |
| **Why does the ESP8266 have a 15-second watchdog?** | If the laptop loses power or Wi-Fi drops, this tabletop prototype switches to a local fixed cycle with yellow and all-red clearance. This is a demonstration fallback, not a certified road-safety system. |
| **What audio features were extracted?** | 20 Mel-Frequency Cepstral Coefficients (MFCCs) representing spectral power on the human auditory scale, plus RMS energy, spectral centroid, and zero-crossing rates. |
| **Why YOLOv8n?** | YOLOv8 nano has only 3.2 million parameters, allowing real-time 25-30 FPS inference directly on a normal laptop CPU without requiring an external GPU. |

---

## 12. License & Acknowledgments

Developed as a college AI + IoT academic project prototype. Built with FastAPI, Ultralytics YOLO, React, ESP8266 Arduino, and 74HC595 shift registers.
