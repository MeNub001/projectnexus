import paho.mqtt.client as mqtt
import json
import streamlit as st
import folium
from streamlit_folium import st_folium
import re
import requests
from engine3_router import AegisDispatcher
import joblib
from datetime import datetime


@st.cache_resource
def load_supply_regressor():
    try:
        return joblib.load("supply_model.pkl")
    except Exception:
        return None


supply_artifact = load_supply_regressor()

st.set_page_config(
    page_title="AEGIS | Incident Command Console",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Military Tactical Dark Theme & Unified Card System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@400;600;700&display=swap');

    .stApp {
        background-color: #060a12;
        background-image: radial-gradient(circle at 50% 0%, #0d192e 0%, #060a12 75%);
        font-family: 'Inter', sans-serif;
        color: #f1f5f9;
    }

    .top-hud {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(13, 22, 38, 0.85);
        border: 1px solid rgba(0, 240, 255, 0.25);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        padding: 10px 20px;
        border-radius: 10px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .top-hud.emergency {
        background: rgba(45, 10, 15, 0.9);
        border: 1px solid #ef4444;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.6);
    }
    .top-hud-title {
        font-family: 'Orbitron', monospace;
        font-size: 18px;
        font-weight: 900;
        letter-spacing: 1.5px;
        color: #00f0ff;
        text-shadow: 0 0 12px rgba(0, 240, 255, 0.5);
    }
    .top-hud.emergency .top-hud-title {
        color: #ef4444;
        text-shadow: 0 0 15px rgba(239, 68, 68, 0.8);
    }
    .hud-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 230, 118, 0.12);
        border: 1px solid #00e676;
        color: #00e676;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 700;
    }
    .hud-badge.emergency {
        background: rgba(239, 68, 68, 0.15);
        border-color: #ef4444;
        color: #ef4444;
    }

    .tactical-card {
        background: rgba(13, 22, 38, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 6px 24px 0 rgba(0, 0, 0, 0.4);
    }
    .tactical-header {
        font-family: 'Orbitron', monospace;
        font-size: 12px;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    textarea {
        background-color: #09111f !important;
        color: #ffffff !important;
        font-size: 13px !important;
        font-family: 'Inter', sans-serif !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 6px !important;
        padding: 8px !important;
    }
    textarea:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.25) !important;
    }

    .log-window {
        background: #04080f;
        border: 1px solid #1e3a5f;
        border-radius: 6px;
        padding: 8px;
        height: 100px;
        overflow-y: auto;
        font-family: 'Orbitron', monospace;
        font-size: 10px;
        color: #00e676;
        margin-top: 8px;
    }
    .log-entry.critical {
        color: #ef4444;
        font-weight: 700;
    }

    div[data-testid="stNumberInput"] label p, 
    div[data-testid="stSelectbox"] label p {
        color: #f8fafc !important; 
        font-weight: 600 !important;
        font-size: 12px !important;
    }

    div.stButton > button:not([kind="primary"]) {
        background-color: #0f1c30 !important;
        color: #f8fafc !important; 
        border: 1px solid #38bdf8 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    div.stButton > button:not([kind="primary"]):hover {
        background-color: #1e293b !important;
        color: #00f0ff !important;
        border-color: #00f0ff !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.3) !important;
    }
    div.stButton > button[kind="primary"] {
        font-family: 'Orbitron', monospace;
        font-weight: 900 !important;
    }

    .shelter-card {
        background: #09111f;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .shelter-card.active-target {
        background: rgba(0, 240, 255, 0.08);
        border: 1px solid #00f0ff;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.15);
    }
    .shelter-card-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .rank-tag {
        font-family: 'Orbitron', monospace;
        font-size: 12px;
        font-weight: 900;
        color: #64748b;
    }
    .rank-tag.active {
        color: #00f0ff;
    }
    .facility-name {
        font-weight: 700;
        font-size: 13px;
        color: #f1f5f9;
    }
    .shelter-card-right {
        display: flex;
        align-items: center;
        gap: 12px;
        text-align: right;
    }
    .target-badge {
        background: rgba(0, 240, 255, 0.2);
        color: #00f0ff;
        border: 1px solid #00f0ff;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 700;
    }
    .queue-badge {
        background: rgba(100, 116, 139, 0.15);
        color: #94a3b8;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 600;
    }
    .alert-hazard {
        background: rgba(239, 68, 68, 0.15);
        border-left: 3px solid #ef4444;
        padding: 8px;
        border-radius: 4px;
        font-size: 11px;
        color: #fca5a5;
        margin-top: 8px;
        font-weight: 600;
    }
    .alert-optimal {
        background: rgba(0, 230, 118, 0.15);
        border-left: 3px solid #00e676;
        padding: 8px;
        border-radius: 4px;
        font-size: 11px;
        color: #86efac;
        margin-top: 8px;
        font-weight: 600;
    }

    .leaflet-control-attribution,
    .leaflet-control-scale {
        display: none !important;
    }
    .leaflet-tile-pane {
        filter: brightness(0.65) invert(1) contrast(2.6) hue-rotate(200deg) saturate(0.25) !important;
    }
    .leaflet-container {
        background: #090e17 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if "dispatcher" not in st.session_state:
    st.session_state.dispatcher = AegisDispatcher()
if "current_transcript" not in st.session_state:
    st.session_state.current_transcript = ""
if "supplies_ledger" not in st.session_state:
    st.session_state.supplies_ledger = {
        "SK Seri Iskandar": {},
        "Dewan Serbaguna Bota": {},
        "Klinik Kesihatan Seri Iskandar": {}
    }
if "sensor_water" not in st.session_state:
    st.session_state.sensor_water = 420  # Baseline mV
if "sensor_gas" not in st.session_state:
    st.session_state.sensor_gas = 85  # Baseline ppm
if "emergency_state" not in st.session_state:
    st.session_state.emergency_state = False
if "sensor_logs" not in st.session_state:
    st.session_state.sensor_logs = [f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM ONLINE. AWAITING TELEMETRY..."]
if "manual_blocked_node" not in st.session_state:
    st.session_state.manual_blocked_node = "None"


# Fetch Live API Data Function
def fetch_live_hardware_data():
    try:
        res = requests.get("http://127.0.0.1:8000/telemetry", timeout=1)
        if res.status_code == 200:
            data = res.json()
            st.session_state.sensor_water = data.get("water", 420)
            st.session_state.sensor_gas = data.get("gas", 85)

            # Automatically declare emergency state if thresholds breached
            if st.session_state.sensor_water > 2000 or st.session_state.sensor_gas > 400:
                st.session_state.emergency_state = True
    except Exception:
        pass  # Silently fail and use existing states if API is offline


LOCATIONS = {
    "Balai Bomba Command Hub": [4.3644, 100.9841],
    "Simpang UTP Junction": [4.3821, 100.9712],
    "Jambatan Bota Kanan": [4.3495, 100.8802],
    "Lebuhraya High Ground Bypass": [4.3912, 100.9405],
    "SK Seri Iskandar": [4.3602, 100.9631],
    "Klinik Kesihatan Seri Iskandar": [4.3580, 100.9754],
    "Dewan Serbaguna Bota": [4.3470, 100.8750]
}


def parse_radio_transmission(text: str) -> dict:
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "aegis-parser",
                "prompt": f"Extract JSON with keys 'shelter', 'evacuees' (int), 'blocked_road', 'critical_need' from: {text}. Output ONLY valid JSON.",
                "format": "json",
                "stream": False
            },
            timeout=15
        )
        parsed = res.json().get("response", "{}")
        import json
        parsed = json.loads(parsed)
    except Exception:
        parsed = {}

    if not parsed.get("shelter"):
        if "Dewan Serbaguna Bota" in text or "Dewan Bota" in text:
            parsed["shelter"] = "Dewan Serbaguna Bota"
        elif "Klinik Kesihatan" in text:
            parsed["shelter"] = "Klinik Kesihatan Seri Iskandar"
        elif "SK Seri Iskandar" in text:
            parsed["shelter"] = "SK Seri Iskandar"

    if not parsed.get("evacuees"):
        evac_match = re.search(r"(\d+)\s+evacuees", text, re.IGNORECASE)
        if evac_match:
            parsed["evacuees"] = int(evac_match.group(1))

    if not parsed.get("blocked_road"):
        hazard_match = re.search(
            r"(Jambatan Bota Kanan|Jambatan Lama|Simpang UTP Junction|Lebuhraya High Ground Bypass|[A-Za-z\s]+)\s+(collapsed|washed away|submerged|impassable|severed|destroyed)",
            text, re.IGNORECASE
        )
        if hazard_match:
            parsed["blocked_road"] = hazard_match.group(1).strip()

    return parsed


# Top HUD Dynamic Render
hud_class = "top-hud emergency" if st.session_state.emergency_state else "top-hud"
badge_class = "hud-badge emergency" if st.session_state.emergency_state else "hud-badge"
badge_text = "EMERGENCY STATE DECLARED" if st.session_state.emergency_state else "MULTI-NODE ARBITRATION ACTIVE"
badge_color = "#ef4444" if st.session_state.emergency_state else "#00e676"

st.markdown(f"""
<div class="{hud_class}">
    <div class="top-hud-title">AEGIS INCIDENT COMMAND CONSOLE</div>
    <div>
        <span class="{badge_class}"><span style="height:6px; width:6px; border-radius:50%; background:{badge_color}; display:inline-block;"></span> {badge_text}</span>
        <span style="margin-left: 10px; font-size:11px; color:#64748b;">SECTOR: PERAK TENGAH</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_telemetry, col_gis = st.columns([1.1, 1], gap="small")

with col_telemetry:
    # --- HARDWARE TELEMETRY & OVERRIDE CARD ---
    st.markdown('<div class="tactical-card">', unsafe_allow_html=True)
    st.markdown('<div class="tactical-header">Hardware Telemetry & Infrastructure Override</div>',
                unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns([1, 1, 1, 1])
    with m1:
        st.metric("Water Level (Analog)", f"{st.session_state.sensor_water} mV",
                  delta="CRITICAL" if st.session_state.sensor_water > 2000 else "Stable", delta_color="inverse")
    with m2:
        st.metric("Gas Level (MQ-x)", f"{st.session_state.sensor_gas} ppm",
                  delta="CRITICAL" if st.session_state.sensor_gas > 400 else "Stable", delta_color="inverse")
    with m3:
        if st.button("🔄 SYNC LIVE DATA", use_container_width=True):
            fetch_live_hardware_data()
            st.session_state.sensor_logs.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] TELEMETRY: Pulled latest hardware state from API.")
            st.rerun()
    with m4:
        if st.button("⚠️ SIMULATE SPIKE", use_container_width=True):
            st.session_state.sensor_water = 2850
            st.session_state.sensor_gas = 610
            st.session_state.emergency_state = True
            st.session_state.manual_blocked_node = "Jambatan Bota Kanan"
            timestamp = datetime.now().strftime('%H:%M:%S')
            st.session_state.sensor_logs.append(
                f"[{timestamp}] CRITICAL: Water {st.session_state.sensor_water}mV | Gas {st.session_state.sensor_gas}ppm")
            st.session_state.sensor_logs.append(f"[{timestamp}] AUTO-OVERRIDE: Jambatan Bota Kanan Severed.")
            st.rerun()

    c_override, c_btn = st.columns([2, 1])
    with c_override:
        override_target = st.selectbox(
            "Manual Corridor Severing",
            ["None"] + list(LOCATIONS.keys()),
            index=(["None"] + list(LOCATIONS.keys())).index(
                st.session_state.manual_blocked_node) if st.session_state.manual_blocked_node in LOCATIONS else 0,
            label_visibility="collapsed"
        )
    with c_btn:
        if st.button("SEVER PATH", use_container_width=True):
            st.session_state.manual_blocked_node = override_target
            if override_target != "None":
                st.session_state.sensor_logs.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] CMD: Manual override severing {override_target}.")
            st.rerun()

    log_html = "".join([f"<div class='log-entry {'critical' if 'CRITICAL' in log else ''}'>{log}</div>" for log in
                        st.session_state.sensor_logs[-5:]])
    st.markdown(f"<div class='log-window'>{log_html}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- COMMAND INPUT CARD ---
    st.markdown('<div class="tactical-card">', unsafe_allow_html=True)
    st.markdown('<div class="tactical-header">Command Input</div>', unsafe_allow_html=True)

    st.caption("Target Facility Selection:")
    loc1, loc2, loc3 = st.columns(3)

    if "selected_shelter" not in st.session_state:
        st.session_state.selected_shelter = "SK Seri Iskandar"

    if loc1.button("SK Seri Iskandar", use_container_width=True):
        st.session_state.selected_shelter = "SK Seri Iskandar"
    if loc2.button("Dewan Bota", use_container_width=True):
        st.session_state.selected_shelter = "Dewan Serbaguna Bota"
    if loc3.button("Klinik Kesihatan", use_container_width=True):
        st.session_state.selected_shelter = "Klinik Kesihatan Seri Iskandar"

    st.markdown(
        f"<div style='font-size: 12px; margin-bottom: 8px;'>Active Selected Shelter: <b>{st.session_state.selected_shelter}</b></div>",
        unsafe_allow_html=True)

    col_victims, col_supplies = st.columns([1, 1.8])
    with col_victims:
        evac_count = st.number_input("Victims", min_value=0, max_value=500, value=80, step=5)
    with col_supplies:
        available_resources = ["Food & Water", "Blankets", "First Aid Kits", "Cholera Kits"]
        resources_needed = st.multiselect(
            "Supplies Needed",
            options=available_resources,
            default=["Food & Water", "First Aid Kits"]
        )

    # ML Inference
    predicted_defaults = {}
    if supply_artifact:
        model = supply_artifact["model"]
        shelter_map = supply_artifact["shelter_mapping"]
        st_code = shelter_map.get(st.session_state.selected_shelter, 0)
        vulnerability_score = 1.8 if st_code == 2 else 1.2
        raw_preds = model.predict([[evac_count, st_code, vulnerability_score, 2]])[0]
        for name, val in zip(supply_artifact["targets"], raw_preds):
            predicted_defaults[name] = max(1, int(round(val)))
    else:
        predicted_defaults = {res: evac_count for res in available_resources}

    calculated_supplies = {}
    if resources_needed:
        st.markdown(
            "<div style='font-size: 11px; font-weight: 700; color: #38bdf8; margin-top: 14px; margin-bottom: 6px;'>REGRESSION ML FORECAST (PREDICTED REQUIREMENT)</div>",
            unsafe_allow_html=True)
        h_col1, h_col2 = st.columns([2, 1.2])
        with h_col1:
            st.markdown(
                "<div style='font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase;'>Supply Item</div>",
                unsafe_allow_html=True)
        with h_col2:
            st.markdown(
                "<div style='font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase;'>Predicted Qty</div>",
                unsafe_allow_html=True)
        st.markdown("<hr style='margin: 4px 0 8px 0; border: none; border-top: 1px solid #1e293b;'>",
                    unsafe_allow_html=True)

        for res in resources_needed:
            r_col1, r_col2 = st.columns([2, 1.2])
            with r_col1: st.markdown(
                f"<div style='padding-top: 7px; font-size: 13px; font-weight: 600; color: #f8fafc;'>{res}</div>",
                unsafe_allow_html=True)
            with r_col2:
                calculated_supplies[res] = st.number_input(f"Qty {res}", min_value=1, max_value=10000,
                                                           value=int(predicted_defaults.get(res, 10)), step=5,
                                                           label_visibility="collapsed")

    lbl_col, btn_upd, btn_clr = st.columns([2, 1, 1])
    with lbl_col:
        st.markdown(
            "<div style='font-size: 11px; font-weight: 600; color: #f8fafc; margin-top: 15px;'>Live Transcript:</div>",
            unsafe_allow_html=True)
    with btn_upd:
        if st.button("UPDATE", type="secondary", use_container_width=True):
            supplies_string = ", ".join([f"{qty} {res}" for res, qty in calculated_supplies.items()])
            st.session_state.current_transcript = f"{st.session_state.selected_shelter} took in {evac_count} evacuees and needs {supplies_string}."
            st.rerun()
    with btn_clr:
        if st.button("CLEAR", type="secondary", use_container_width=True):
            st.session_state.current_transcript = ""
            st.rerun()

    radio_input = st.text_area("Live Transcript", value=st.session_state.current_transcript, height=60,
                               label_visibility="collapsed")

    st.write("")
    btn_calc, btn_rst2 = st.columns([2.5, 1])

    with btn_calc:
        manual_submit = st.button("EXECUTE MISSION ROUTING", type="primary", use_container_width=True)
    with btn_rst2:
        if st.button("SYSTEM RESET", type="secondary", use_container_width=True):
            st.session_state.dispatcher = AegisDispatcher()
            st.session_state.supplies_ledger = {"SK Seri Iskandar": {}, "Dewan Serbaguna Bota": {},
                                                "Klinik Kesihatan Seri Iskandar": {}}
            st.session_state.sensor_water = 420
            st.session_state.sensor_gas = 85
            st.session_state.emergency_state = False
            st.session_state.manual_blocked_node = "None"
            st.session_state.sensor_logs = [
                f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM ONLINE. AWAITING TELEMETRY..."]
            if "last_plan" in st.session_state: del st.session_state.last_plan
            if "last_extracted" in st.session_state: del st.session_state.last_extracted
            st.rerun()

    if manual_submit:
        with st.spinner("Processing routing and node overrides..."):
            extracted = parse_radio_transmission(radio_input)
            target = st.session_state.selected_shelter

            if st.session_state.manual_blocked_node != "None":
                extracted["blocked_road"] = st.session_state.manual_blocked_node

            for res, qty in calculated_supplies.items():
                if res in st.session_state.supplies_ledger[target]:
                    st.session_state.supplies_ledger[target][res] += qty
                else:
                    st.session_state.supplies_ledger[target][res] = qty

            ledger = st.session_state.supplies_ledger[target]
            extracted["critical_need"] = " | ".join([f"{qty} {sup}" for sup, qty in ledger.items()])

            plan = st.session_state.dispatcher.process_incident(extracted)
            st.session_state.last_extracted = extracted
            st.session_state.last_plan = plan

            # --- UPDATED MQTT TRANSMISSION & LOGGING BLOCK ---
            try:
                cmd_client = mqtt.Client()
                cmd_client.connect("10.204.132.164", 1883, 60)
                route_payload = json.dumps({"mission_route": plan["calculated_route"]})
                cmd_client.publish("aegis/rover/route", route_payload)
                cmd_client.disconnect()

                # Append the successful transmission to the dashboard's log window
                timestamp = datetime.now().strftime('%H:%M:%S')
                route_str = " ➔ ".join(plan["calculated_route"])
                st.session_state.sensor_logs.append(f"[{timestamp}] ROVER UPLINK: Trajectory [{route_str}]")

            except Exception as e:
                # Log any connection failures as critical errors
                timestamp = datetime.now().strftime('%H:%M:%S')
                st.session_state.sensor_logs.append(f"[{timestamp}] CRITICAL: Rover comms failure ({e})")

            # Force a UI refresh so the log window at the top updates immediately
            st.rerun()
            # -------------------------------------------------

    st.markdown('</div>', unsafe_allow_html=True)

with col_gis:
    st.markdown('<div class="tactical-header">Tactical Operations Map</div>', unsafe_allow_html=True)

    m = folium.Map(
        location=[4.3700, 100.9300],
        zoom_start=12,
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="Tactical Operations Grid",
        control_scale=False,
        attributionControl=False
    )

    dispatcher = st.session_state.dispatcher
    active_route = st.session_state.get("last_plan", {}).get("calculated_route", [])

    for u, v in dispatcher.G.edges():
        if u in LOCATIONS and v in LOCATIONS:
            folium.PolyLine(
                locations=[LOCATIONS[u], LOCATIONS[v]],
                color="#64748b",
                weight=3,
                dash_array="6, 6",
                opacity=0.85
            ).add_to(m)

    if len(active_route) > 1:
        route_coords = [LOCATIONS[node] for node in active_route if node in LOCATIONS]
        folium.PolyLine(
            locations=route_coords,
            color="#00e676",
            weight=6,
            opacity=0.95,
            tooltip="Autonomous Primary Mission Corridor"
        ).add_to(m)

    for name, coords in LOCATIONS.items():
        is_primary = (name == st.session_state.get("last_plan", {}).get("selected_target"))
        is_blocked = (name == st.session_state.get("last_extracted", {}).get("blocked_road"))

        if is_primary:
            icon_color, icon_name = "red", "flag"
        elif is_blocked:
            icon_color, icon_name = "black", "ban"
        elif "Command Hub" in name:
            icon_color, icon_name = "blue", "home"
        else:
            icon_color, icon_name = "cadetblue", "info-sign"

        folium.Marker(
            location=coords,
            popup=folium.Popup(f"<b>{name}</b>", max_width=200),
            tooltip=f"Facility: {name}",
            icon=folium.Icon(color=icon_color, icon=icon_name)
        ).add_to(m)

    st_folium(m, width="100%", height=295)
    st.markdown('</div>', unsafe_allow_html=True)

    if "last_plan" in st.session_state:
        plan = st.session_state.last_plan
        extracted = st.session_state.last_extracted

        st.markdown('<div class="tactical-card">', unsafe_allow_html=True)
        st.markdown('<div class="tactical-header">Multi-Shelter Priority Arbitration</div>', unsafe_allow_html=True)

        for i, item in enumerate(plan["rankings"]):
            is_winner = (item["shelter"] == plan["selected_target"])
            card_class = "active-target" if is_winner else ""
            rank_class = "active" if is_winner else ""
            badge_html = "<span class='target-badge'>ACTIVE TARGET</span>" if is_winner else "<span class='queue-badge'>STANDBY</span>"

            shelter_name = item["shelter"]
            if shelter_name in st.session_state.supplies_ledger and st.session_state.supplies_ledger[shelter_name]:
                ledger_items = st.session_state.supplies_ledger[shelter_name]
                supply_tag = " | ".join([f"{qty} {sup}" for sup, qty in ledger_items.items()])
            else:
                supply_tag = "Standard Rations"

            st.markdown(f"""
            <div class="shelter-card {card_class}">
                <div class="shelter-card-left">
                    <span class="rank-tag {rank_class}">#{i + 1}</span>
                    <div>
                        <div class="facility-name">{item['shelter']}</div>
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">
                            {item['evacuees']} pax <span style="color: #475569;">|</span> <span style="color: #cbd5e1;">{supply_tag}</span>
                        </div>
                    </div>
                </div>
                <div class="shelter-card-right">
                    {badge_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        if extracted.get("blocked_road"):
            st.markdown(
                f'<div class="alert-hazard">HAZARD OVERRIDE: Infrastructure [{extracted["blocked_road"]}] severed from map routing algorithm.</div>',
                unsafe_allow_html=True)

        st.markdown(
            f'<div class="alert-optimal">TRAJECTORY: Base ➔ {" ➔ ".join(plan["calculated_route"])} ({plan["latency_ms"]} ms)</div>',
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)