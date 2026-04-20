import asyncio
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from simulation import simulation_engine
from detection import detector
from models import SystemStatus
import sqlite3
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/petropulse.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            type TEXT,
            severity TEXT,
            message TEXT,
            zone TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            message TEXT,
            zone TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app = FastAPI(title="PetroPulse API")

# Add CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for the latest state and alerts
state = {
    "latest_data": {},
    "active_alerts": [],
    "status": "Normal"
}

@app.get("/")
async def root():
    return {"message": "PetroPulse API is running"}

@app.get("/status")
async def get_status():
    return state

@app.post("/trigger/{event_type}")
async def trigger_event(event_type: str, active: bool):
    if event_type == "leak":
        simulation_engine.trigger_leak(active)
    elif event_type == "theft":
        simulation_engine.trigger_theft(active)
    return {"message": f"{event_type} simulation {'started' if active else 'stopped'}"}

@app.post("/report")
async def add_report(report: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO reports (timestamp, message, zone) VALUES (?, ?, ?)",
        (timestamp, report.get("message"), report.get("zone"))
    )
    conn.commit()
    conn.close()
    
    # Also inject into live alerts for demo visibility
    state["active_alerts"].append({
        "id": "report-" + str(len(state["active_alerts"])),
        "timestamp": timestamp,
        "type": "Community Report",
        "severity": "Info",
        "message": report.get("message", "Incident reported by community"),
        "zone": report.get("zone", "General")
    })
    return {"status": "Report received"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Send historical alerts from DB on connection
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, type, severity, message, zone FROM alerts ORDER BY timestamp DESC LIMIT 10")
        rows = cursor.fetchall()
        historical_alerts = []
        for row in rows:
            historical_alerts.append({
                "id": row[0], "timestamp": row[1], "type": row[2], 
                "severity": row[3], "message": row[4], "zone": row[5]
            })
        
        # Also include community reports
        cursor.execute("SELECT timestamp, message, zone FROM reports ORDER BY timestamp DESC LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            historical_alerts.append({
                "id": "hist-report-" + str(uuid.uuid4())[:8],
                "timestamp": row[0], "type": "Community Report", 
                "severity": "Info", "message": row[1], "zone": row[2]
            })
        
        # Sort combined historical data
        historical_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        state["active_alerts"] = historical_alerts[:10]
        conn.close()
    except Exception as e:
        print(f"Error fetching history: {e}")

    try:
        while True:
            # Get latest data from simulation
            current_data = simulation_engine.get_latest_data()
            
            # Run detection logic
            new_alerts = detector.analyze(current_data)
            if new_alerts:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                for alert in new_alerts:
                    cursor.execute(
                        "INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?)",
                        (alert["id"], alert["timestamp"], alert["type"], alert["severity"], alert["message"], alert["zone"])
                    )
                conn.commit()
                conn.close()
                
                state["active_alerts"].extend(new_alerts)
                state["status"] = "Risk" if any(a["severity"] == "Critical" for a in new_alerts) else state["status"]
            
            # Clean up alerts (keep only last 10)
            if len(state["active_alerts"]) > 10:
                state["active_alerts"] = state["active_alerts"][-10:]

            # Update state
            state["latest_data"] = current_data
            
            # Send to client
            await websocket.send_json({
                "data": current_data,
                "alerts": state["active_alerts"],
                "status": state["status"]
            })
            
            await asyncio.sleep(1)  # 1 second update interval
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
