import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from simulation import simulation_engine
from detection import detector
from models import SystemStatus
from database import init_db, SessionLocal, AlertDB, ReportDB
import os
import uuid

# Initialize database tables
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
    db = SessionLocal()
    try:
        timestamp = datetime.now().isoformat()
        new_report = ReportDB(
            timestamp=timestamp,
            message=report.get("message"),
            zone=report.get("zone")
        )
        db.add(new_report)
        db.commit()
    finally:
        db.close()
    
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
    db = SessionLocal()
    try:
        # Fetch last 10 alerts
        historical_alerts_db = db.query(AlertDB).order_by(AlertDB.timestamp.desc()).limit(10).all()
        historical_alerts = []
        for alert in historical_alerts_db:
            historical_alerts.append({
                "id": alert.id, "timestamp": alert.timestamp, "type": alert.type, 
                "severity": alert.severity, "message": alert.message, "zone": alert.zone
            })
        
        # Also include last 5 community reports
        historical_reports_db = db.query(ReportDB).order_by(ReportDB.timestamp.desc()).limit(5).all()
        for report in historical_reports_db:
            historical_alerts.append({
                "id": "hist-report-" + str(uuid.uuid4())[:8],
                "timestamp": report.timestamp, "type": "Community Report", 
                "severity": "Info", "message": report.message, "zone": report.zone
            })
        
        # Sort combined historical data
        historical_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        state["active_alerts"] = historical_alerts[:10]
    except Exception as e:
        print(f"Error fetching history: {e}")
    finally:
        db.close()

    try:
        while True:
            # Get latest data from simulation
            current_data = simulation_engine.get_latest_data()
            
            # Run detection logic
            new_alerts = detector.analyze(current_data)
            if new_alerts:
                db = SessionLocal()
                try:
                    for alert in new_alerts:
                        db_alert = AlertDB(
                            id=alert["id"],
                            timestamp=alert["timestamp"],
                            type=alert["type"],
                            severity=alert["severity"],
                            message=alert["message"],
                            zone=alert["zone"]
                        )
                        db.add(db_alert)
                    db.commit()
                finally:
                    db.close()
                
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
        print(f"Error in websocket loop: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    # Use environment PORT for Render compatibility
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
