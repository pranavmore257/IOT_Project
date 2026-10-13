# Smart Acoustic & Vision Traffic Signal

> **Real-Time Multimodal AI Traffic Signal Management using Audio, Video, and ESP32 IoT Prototype**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/Vision%20AI-Ultralytics%20YOLOv8n-FF6F00.svg)](https://docs.ultralytics.com/)
[![Audio AI](https://img.shields.io/badge/Audio%20AI-MFCC%20%2B%20Random%20Forest%20(96.7%25)-green.svg)]()
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite%20%2B%20Tailwind-61DAFB.svg)](https://vitejs.dev/)
[![ESP32](https://img.shields.io/badge/IoT%20Hardware-ESP32%20(12--LED%20Array)-E7352C.svg)](https://www.espressif.com/)

---

## 1. Project Overview

The **Smart Acoustic & Vision Traffic Signal** is a college-level AI + IoT prototype demonstrating how real-time computer vision, acoustic artificial intelligence, a multimodal decision engine, and an ESP32-based microcontroller work synchronously to manage traffic at a 4-way intersection.

> [!NOTE]
> **Prototype Scope:** This is an academic research prototype controlling a physical miniature 12-LED 4-way intersection. It demonstrates smart city concepts on miniature breadboard hardware and real-time dashboard software.

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
                     |        ESP32 IoT Controller       |
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

## 4. Hardware Requirements & Pin Mapping

### Required Hardware
* **1x ESP32 Development Board** (NodeMCU-32S / ESP-WROOM-32)
* **4x Red LEDs, 4x Yellow LEDs, 4x Green LEDs** (12 LEDs total for 4 directions)
* **12x 220Ω Resistors**
* **1x Breadboard & Jumper Wires**
* **1x USB Cable**
* **1x Laptop Webcam & Microphone**

### ESP32 GPIO Pin Configuration
Configured at the top of [`esp32/traffic_signal/traffic_signal.ino`](file:///c:/Users/ACER/Downloads/ProjectIoT/esp32/traffic_signal/traffic_signal.ino):

| Intersection Approach | Red LED | Yellow LED | Green LED | Resistor |
| :--- | :---: | :---: | :---: | :---: |
| **NORTH Approach** | GPIO 23 | GPIO 22 | GPIO 21 | 220 Ω |
| **SOUTH Approach** | GPIO 19 | GPIO 18 | GPIO 5  | 220 Ω |
| **EAST Approach**  | GPIO 17 | GPIO 16 | GPIO 4  | 220 Ω |
| **WEST Approach**  | GPIO 0  | GPIO 2  | GPIO 15 | 220 Ω |
| **Optional Buzzer**| GPIO 13 | — | — | Active High |

> [!TIP]
> **ESP32 Disconnected?** The system automatically switches to **SIMULATION MODE** on the dashboard. The project will run smoothly even without the physical microcontroller attached!

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
2. **Observe System Status:** Check top status bar badges (Webcam, Mic, Backend, ESP32, MQTT).
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
   * **ESP32:** Conflicting East/West immediately receives safe yellow clearance before North turns solid GREEN!
9. **Demonstrate Case 4 (Accident Safety Hold):** Click `[ Accident Sound ]`. Crash audio signature triggers immediate **ACCIDENT ALERT** and safe all-RED hold.
10. **Clear & Reset:** Click `[ Reset to Live ]`. The system cycles through yellow clearance and safely resumes normal routine 4-way traffic.
11. **View SQLite Event History:** Scroll down to the SQLite table to show all logged decisions, scores, and timestamps.
12. **Open Viva Specs Modal:** Click `[ AI Models & Viva Specs ]` in the top header to explain model architecture and formulas to the examiner.

---

## 9. ESP32 Firmware Flashing

1. Open `esp32/traffic_signal/traffic_signal.ino` in the **Arduino IDE**.
2. Install required libraries via Library Manager:
   * `ArduinoJson` (v6 or v7)
   * `PubSubClient` (by Nick O'Leary)
3. Set your Wi-Fi SSID, Password, and your Laptop's Local IP address:
   ```cpp
   const char* WIFI_SSID     = "YOUR_WIFI_NAME";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* MQTT_BROKER   = "192.168.1.100"; // Laptop IP running backend
   ```
4. Select board **ESP32 Dev Module** and click **Upload**.
5. Open Serial Monitor at `115200` baud.

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
| **Why does the ESP32 have a 15-second watchdog?** | If the laptop loses power or Wi-Fi drops, city signals must not freeze. The ESP32 detects heartbeat loss and runs an autonomous local fixed cycle with safe yellow clearance. |
| **What audio features were extracted?** | 20 Mel-Frequency Cepstral Coefficients (MFCCs) representing spectral power on the human auditory scale, plus RMS energy, spectral centroid, and zero-crossing rates. |
| **Why YOLOv8n?** | YOLOv8 nano has only 3.2 million parameters, allowing real-time 25-30 FPS inference directly on a normal laptop CPU without requiring an external GPU. |

---

## 12. License & Acknowledgments

Developed as a college AI + IoT academic project prototype. Built with FastAPI, Ultralytics YOLO, React, and ESP32 Arduino.
