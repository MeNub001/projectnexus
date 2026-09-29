from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AEGIS Backend API")

# In-memory storage for live hardware telemetry
live_telemetry = {
    "water": 420,  # default baseline mV
    "gas": 85      # default baseline ppm
}

class TelemetryData(BaseModel):
    sensor: str
    value: int

@app.post("/telemetry")
def update_telemetry(data: TelemetryData):
    if data.sensor in live_telemetry:
        live_telemetry[data.sensor] = data.value
        return {"status": "success", "data": live_telemetry}
    raise HTTPException(status_code=400, detail="Unknown sensor")

@app.get("/telemetry")
def get_telemetry():
    return live_telemetry