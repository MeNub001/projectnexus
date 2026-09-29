import json
import re
import requests
from engine3_router import AegisDispatcher

def extract_with_safety_guard(text: str) -> dict:
    # 1. Primary: Local LLM (Engine 2)
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "aegis-parser",
            "prompt": text,
            "format": "json",
            "stream": False
        },
        timeout=15
    )
    parsed = json.loads(response.json()["response"])

    # 2. Safety Interceptor: Catch missed hazard keywords
    if not parsed.get("blocked_road"):
        hazard_match = re.search(
            r"([A-Za-z\s]+)\s+(collapsed|washed away|submerged|impassable|severed|destroyed)",
            text,
            re.IGNORECASE
        )
        if hazard_match:
            parsed["blocked_road"] = hazard_match.group(1).strip()
            print(f"[SAFETY INTERCEPTOR] LLM missed hazard; recovered: '{parsed['blocked_road']}'")

    return parsed

def run_pipeline(incoming_radio_audio_transcript: str):
    print("\n" + "="*60)
    print(f"[TRANSCRIPT RECEIVED]: \"{incoming_radio_audio_transcript}\"")
    print("="*60)

    # Run Engine 2 + Safety Guard
    parsed = extract_with_safety_guard(incoming_radio_audio_transcript)
    print("\n[ENGINE 2 OUTPUT - PARSED DATA]:")
    print(json.dumps(parsed, indent=2))

    # Run Engine 3: Routing & Fairness Allocation
    dispatcher = AegisDispatcher()
    dispatch_plan = dispatcher.process_incident(parsed)

    print("\n[ENGINE 3 OUTPUT - PHYSICAL DISPATCH MISSION]:")
    print(f"-> Selected Shelter Destination : {dispatch_plan['target_shelter']}")
    print(f"-> Vulnerability Priority Index  : {dispatch_plan['priority_index']}")
    print(f"-> Calculated Safe Trajectory    : {' -> '.join(dispatch_plan['calculated_route'])}")
    print(f"-> Trajectory Status             : {dispatch_plan['execution_status']}")
    print(f"-> Path Calculation Latency      : {dispatch_plan['latency_ms']} ms")

if __name__ == "__main__":
    run_pipeline("Attention Base, Jambatan Lama collapsed! SK Sri Iskandar took in 60 evacuees and needs cholera kits.")