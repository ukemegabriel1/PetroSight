import sqlite3
import os
from datetime import datetime, timedelta
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/petrosight.db")

def load_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure tables exist (redundant but safe)
    cursor.execute('CREATE TABLE IF NOT EXISTS alerts (id TEXT PRIMARY KEY, timestamp TEXT, type TEXT, severity TEXT, message TEXT, zone TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, message TEXT, zone TEXT)')

    # Add 5 Sample Alerts
    now = datetime.now()
    sample_alerts = [
        (str(uuid.uuid4()), (now - timedelta(hours=2)).isoformat(), "Pressure Spike", "Warning", "High pressure detected in Pipeline 04.", "Zone B"),
        (str(uuid.uuid4()), (now - timedelta(hours=5)).isoformat(), "Leak Detected", "Critical", "Automated shutoff triggered due to rapid decompression.", "Zone A"),
        (str(uuid.uuid4()), (now - timedelta(days=1)).isoformat(), "Suspected Theft", "Warning", "Flow mismatch on terminal 02.", "Terminal 02"),
        (str(uuid.uuid4()), (now - timedelta(days=1, hours=4)).isoformat(), "Maintenance", "Info", "Regular sensor calibration completed.", "Zone C"),
        (str(uuid.uuid4()), (now - timedelta(days=2)).isoformat(), "Leak Detected", "Critical", "Static pressure failure.", "Zone A")
    ]

    cursor.executemany("INSERT OR IGNORE INTO alerts VALUES (?, ?, ?, ?, ?, ?)", sample_alerts)

    # Add 3 Sample Community Reports
    sample_reports = [
        ((now - timedelta(hours=1)).isoformat(), "Minor oil sheen spotted near the creek.", "Zone A South"),
        ((now - timedelta(hours=12)).isoformat(), "Fence damaged near terminal entrance.", "Terminal 02"),
        ((now - timedelta(days=3)).isoformat(), "Unusual vibration in secondary pump.", "Zone C")
    ]

    cursor.executemany("INSERT INTO reports (timestamp, message, zone) VALUES (?, ?, ?)", sample_reports)

    conn.commit()
    print(f"Successfully loaded {len(sample_alerts)} alerts and {len(sample_reports)} reports into {DB_PATH}")
    conn.close()

if __name__ == "__main__":
    load_data()
