# 🛰️ Project NEXUS: Digital Twin Disaster Response & Autonomous Routing System

**Project NEXUS** is an end-to-end, real-time digital twin disaster response and evacuation management system designed for tactical operations in Perak Tengah. It bridges physical Internet of Things (IoT) hardware sensors, an MQTT communication broker, a local AI-driven Natural Language Processing (NLP) engine, machine learning regression models, and a GIS-enabled Streamlit command console to automate crisis logistics and autonomous rover dispatch.

---

## 🏗️ System Architecture & Components

The pipeline operates across four core layers:
1. **IoT Hardware Layer:** ESP32 microcontrollers acting as data mules (`commandcentre`) and autonomous rovers (`rover`) equipped with analog water level sensors and MQ gas sensors.
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
├── commandcentre/
│   └── commandcentre.ino      # ESP32 Data Mule firmware (Water/Gas sensors & MQTT publish)
├── rover/
│   └── rover.ino              # ESP32 Autonomous Rover firmware (MQTT command subscriber)
├── dashboard.py               # Streamlit Incident Command Console UI & GIS Map
├── engine3_router.py          # NetworkX routing engine & AegisDispatcher class
├── server.py                  # FastAPI backend wrapper for telemetry & API endpoints
├── mqtt_bridge.py             # Real-time MQTT-to-API telemetry bridge
├── Modelfile                  # Configuration blueprint for Ollama aegis-parser
├── supply_model.pkl           # Trained Random Forest regressor for supply forecasting
├── my_flood_model.json        # XGBoost flood prediction artifact
├── full_pipeline.py           # End-to-end integration testing script
├── test_engines.py            # Standalone diagnostic test script
└── train_supply_model.py      # Machine learning training script for supply needs
