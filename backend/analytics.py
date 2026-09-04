import sqlite3
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent
ANALYTICS_DB = BASE_DIR / "data" / "analytics.db"


def init_analytics_db():
    ANALYTICS_DB.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(ANALYTICS_DB) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                device_type TEXT,
                category TEXT,
                scripture_reference TEXT,
                response_time_ms INTEGER
            )
            """
        )

        connection.commit()


def track_event(
    event,
    session_id=None,
    device_type=None,
    category=None,
    scripture_reference=None,
    response_time_ms=None,
):
    with sqlite3.connect(ANALYTICS_DB) as connection:
        connection.execute(
            """
            INSERT INTO analytics_events (
                event,
                timestamp,
                session_id,
                device_type,
                category,
                scripture_reference,
                response_time_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event,
                datetime.now(timezone.utc).isoformat(),
                session_id,
                device_type,
                category,
                scripture_reference,
                response_time_ms,
            ),
        )

        connection.commit()