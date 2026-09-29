# 🛰️ Project NEXUS: Digital Twin Disaster Response & Autonomous Routing System

**Project NEXUS** is an end-to-end, real-time digital twin disaster response and evacuation management system designed for tactical operations in **Perak Tengah**. It bridges physical Internet of Things (IoT) hardware sensors, an MQTT communication broker, a local AI-driven Natural Language Processing (NLP) engine, machine learning regression models, and a GIS-enabled Streamlit command console to automate crisis logistics and autonomous rover dispatch.

---

## 🏗️ System Architecture & Components

The pipeline operates across four core layers:

1. **IoT Hardware Layer:** ESP32 microcontrollers acting as data mules and autonomous rovers equipped with analog water level sensors and MQ gas sensors.
2. **Communication Layer:** Mosquitto MQTT broker and Python bridging scripts (`mqtt_bridge.py`) that ingest telemetry and translate sensor spikes into structured disaster events.
3. **Intelligence Layer:**
* **Engine 1 & 2 (NLP Parser):** A local LLM running via Ollama (`aegis-parser`) configured via a strict `Modelfile` to parse messy radio transcripts into clean JSON entities.
* **Engine 3 (Routing & Arbitration):** A FastAPI backend (`server.py`) utilizing NetworkX (`engine3_router.py`) to manage road network graphs, compute A* optimal safe routes, and calculate Social Equity Priority Indices.


* **Supply Predictor:** A trained Random Forest machine learning model (`supply_model.pkl`) that forecasts shelter supply requirements based on evacuee counts.


4. **Command & Control Layer:** A military-themed Streamlit GIS dashboard (`dashboard.py`) featuring Folium interactive maps, live telemetry logs, and real-time mission arbitration.



---

## 📂 Project File Structure

```text
Project NEXUS/
├── dashboard.py             # Streamlit Incident Command Console UI & GIS Map
├── engine3_router.py        # NetworkX routing engine & AegisDispatcher class
├── server.py                # FastAPI backend wrapper for telemetry & API endpoints
├── mqtt_bridge.py           # Real-time MQTT-to-API telemetry bridge
├── Modelfile                # Configuration blueprint for Ollama aegis-parser
├── supply_model.pkl         # Trained Random Forest regressor for supply forecasting
├── my_flood_model.json      # XGBoost flood prediction artifact
├── full_pipeline.py         # End-to-end integration testing script
├── test_engines.py          # Standalone diagnostic test script
└── train_supply_model.py    # Machine learning training script for supply needs

```

---

## ⚙️ Installation & Prerequisites

### 1. Python Dependencies

Install the required libraries inside your active virtual environment:

```bash
pip install fastapi uvicorn paho-mqtt streamlit folium streamlit-folium requests joblib networkx scikit-learn

```

### 2. Local AI Setup (Ollama)

1. Download and install [Ollama](https://ollama.com).
2. Build your custom parsing engine using the project's `Modelfile`:
```bash
ollama create aegis-parser -f Modelfile

```



---

## 🚀 Simultaneous Run Sequence

To bring the entire digital twin system online, launch each service in a **separate terminal window**:

* **Terminal 1: MQTT Broker**
```bash
mosquitto -c "C:\Program Files\mosquitto\mosquitto.conf" -v

```


* **Terminal 2: FastAPI Backend API**
```bash
uvicorn server:app --host 0.0.0.0 --port 8000

```


* **Terminal 3: MQTT-to-Dashboard Bridge**
```bash
python mqtt_bridge.py

```


* **Terminal 4: GIS Incident Command Console**
```bash
streamlit run dashboard.py

```



---

## 🔌 Hardware Pinout (ESP32 Rover & Data Mule)

For physical deployments using an L298N Dual H-Bridge motor driver and sensor modules:

| Component / Signal | ESP32 GPIO Pin | L298N / Sensor Pin | Description |
| --- | --- | --- | --- |
| **Left Motor Speed (PWM)** | `GPIO 25` | `ENA` | Controls left wheel velocity |
| **Left Motor Direction 1** | `GPIO 26` | `IN1` | Left forward control |
| **Left Motor Direction 2** | `GPIO 27` | `IN2` | Left reverse control |
| **Right Motor Direction 1** | `GPIO 32` | `IN3` | Right forward control |
| **Right Motor Direction 2** | `GPIO 33` | `IN4` | Right reverse control |
| **Right Motor Speed (PWM)** | `GPIO 14` | `ENB` | Controls right wheel velocity |
| **Water Sensor (Analog)** | `GPIO 34` | `AO` | Water level analog input |
| **MQ Gas Sensor (Analog)** | `GPIO 35` | `AO` | Air quality / gas hazard detection |
| **System Ground** | `GND` | `GND` | Common ground tie (Critical) |

---

## 🛡️ License & Acknowledgments

Developed for real-time disaster management, multi-sector humanitarian arbitration, and autonomous field robotics under **Project NEXUS**.
