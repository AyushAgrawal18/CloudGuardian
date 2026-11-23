
import json
import sqlite3
from pathlib import Path


class MetricBuffer:
    def __init__(self, db_path: str = "agent/storage/metrics_buffer.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialize_database()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_database(self):
        with self._get_connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS pending_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def add(self, payload: dict):
        with self._get_connection() as connection:
            connection.execute(
                "INSERT INTO pending_metrics (payload) VALUES (?)",
                (json.dumps(payload),),
            )

    def get_pending(self, limit: int = 100) -> list[dict]:
        with self._get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, payload
                FROM pending_metrics
                ORDER BY id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {"id": row[0], "payload": json.loads(row[1])}
            for row in rows
        ]

    def remove(self, metric_id: int):
        with self._get_connection() as connection:
            connection.execute(
                "DELETE FROM pending_metrics WHERE id = ?",
                (metric_id,),
            )

    def count(self) -> int:
        with self._get_connection() as connection:
            return connection.execute(
                "SELECT COUNT(*) FROM pending_metrics"
            ).fetchone()[0]
