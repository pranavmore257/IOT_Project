import sqlite3
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.config.settings import CONFIG

DB_FILE = Path(CONFIG.get("database", {}).get("db_path", "traffic_events.db"))
_lock = threading.Lock()

def init_db():
    with _lock:
        conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                audio_class TEXT,
                audio_confidence REAL,
                video_class TEXT,
                video_confidence REAL,
                vehicle_count INTEGER DEFAULT 0,
                density TEXT,
                direction TEXT,
                decision TEXT,
                signal_state TEXT,
                mode TEXT
            )
        """)
        conn.commit()
        conn.close()

# Ensure table exists on import
init_db()

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def log_event(
    event_type: str,
    audio_class: Optional[str] = None,
    audio_confidence: Optional[float] = None,
    video_class: Optional[str] = None,
    video_confidence: Optional[float] = None,
    vehicle_count: int = 0,
    density: Optional[str] = None,
    direction: Optional[str] = None,
    decision: Optional[str] = None,
    signal_state: Optional[str] = None,
    mode: Optional[str] = "NORMAL"
) -> int:
    with _lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO traffic_events (
                timestamp, event_type, audio_class, audio_confidence,
                video_class, video_confidence, vehicle_count, density,
                direction, decision, signal_state, mode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now, event_type, audio_class, audio_confidence,
            video_class, video_confidence, vehicle_count, density,
            direction, decision, signal_state, mode
        ))
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id

def get_recent_events(limit: int = 50) -> List[Dict[str, Any]]:
    with _lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, event_type, audio_class, audio_confidence,
                   video_class, video_confidence, vehicle_count, density,
                   direction, decision, signal_state, mode
            FROM traffic_events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

def clear_events():
    with _lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM traffic_events")
        conn.commit()
        conn.close()
