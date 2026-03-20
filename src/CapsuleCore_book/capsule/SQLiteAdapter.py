import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from ..core import Entry, Relation
from .Lexicon import Lexicon


class SQLiteAdapter(Lexicon):
    def __init__(self, db_path: str = "codex.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        with self._get_connection() as conn:
            # Tabla de Entradas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    tags TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT
                )
            """)
            # Tabla de Relaciones (con llaves foráneas opcionales para integridad)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relations (
                    from_id TEXT,
                    to_id TEXT,
                    connection_type TEXT,
                    PRIMARY KEY (from_id, to_id, connection_type),
                    FOREIGN KEY (from_id) REFERENCES entries (id) ON DELETE CASCADE,
                    FOREIGN KEY (to_id) REFERENCES entries (id) ON DELETE CASCADE
                )
            """)

    def save(self, entry: Entry) -> None:
        """Upsert: Crea o actualiza la entrada completa."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO entries (id, title, content, tags, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    content=excluded.content,
                    tags=excluded.tags,
                    updated_at=excluded.updated_at,
                    metadata=excluded.metadata
            """,
                (
                    entry.id,
                    entry.title,
                    entry.content,
                    json.dumps(entry.tags),
                    entry.created_at.isoformat(),
                    entry.updated_at.isoformat() if entry.updated_at else None,
                    json.dumps(entry.metadata),
                ),
            )

    def delete(self, entry_id: str) -> bool:
        """Elimina una entrada y sus relaciones asociadas."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            # También limpiamos las relaciones donde participaba esta entrada
            conn.execute(
                "DELETE FROM relations WHERE from_id = ? OR to_id = ?",
                (entry_id, entry_id),
            )
            return cursor.rowcount > 0

    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM entries WHERE id = ?", (entry_id,)
            ).fetchone()
            if not row:
                return None

            return Entry(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                tags=json.loads(row["tags"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"])
                if row["updated_at"]
                else None,
                metadata=json.loads(row["metadata"]),
            )

    def find_by_tag(self, tag: str) -> List[Entry]:
        """Busca entradas que contengan el tag específico en su JSON."""
        with self._get_connection() as conn:
            # Usamos LIKE para buscar dentro del string JSON de tags
            search_pattern = f'%"{tag.lower().strip()}"%'
            rows = conn.execute(
                "SELECT * FROM entries WHERE tags LIKE ?", (search_pattern,)
            ).fetchall()

            entries = []
            for row in rows:
                entries.append(
                    Entry(
                        id=row["id"],
                        title=row["title"],
                        content=row["content"],
                        tags=json.loads(row["tags"]),
                        created_at=datetime.fromisoformat(row["created_at"]),
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                        metadata=json.loads(row["metadata"]),
                    )
                )
            return entries

    def add_relation(self, relation: Relation) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO relations (from_id, to_id, connection_type) VALUES (?, ?, ?)",
                (relation.from_id, relation.to_id, relation.connection_type),
            )

    def remove_relation(self, relation: Relation) -> None:
        """Elimina una conexión específica entre dos entradas."""
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM relations WHERE from_id = ? AND to_id = ? AND connection_type = ?",
                (relation.from_id, relation.to_id, relation.connection_type),
            )
