"""
Database management module for Classroom Management System (CMS).
Handles SQLite connection, schema initialization, seeding, and execution helpers.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union

DEFAULT_DB_FILE = os.path.join(os.path.dirname(__file__), "cms.db")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")
SEED_FILE = os.path.join(os.path.dirname(__file__), "seed_data.sql")


class Database:
    """Manages SQLite database connections and query operations."""

    def __init__(self, db_path: str = DEFAULT_DB_FILE):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a configured sqlite3 connection with Row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self, seed: bool = True) -> None:
        """Initialize database tables, views, and indexes from schema.sql."""
        if not os.path.exists(SCHEMA_FILE):
            raise FileNotFoundError(f"Schema file not found at: {SCHEMA_FILE}")

        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema_sql)

        if seed:
            self.seed_database()

    def seed_database(self) -> None:
        """Populate database with sample seed data if seed_data.sql exists."""
        if os.path.exists(SEED_FILE):
            with open(SEED_FILE, "r", encoding="utf-8") as f:
                seed_sql = f.read()
            with self.get_connection() as conn:
                conn.executescript(seed_sql)

    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return the lastrowid or rowcount."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def executemany(self, query: str, params_list: List[Tuple[Any, ...]]) -> int:
        """Execute a parameterized query across multiple param sets."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

    def fetchall(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return all matching rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetchone(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        """Execute a SELECT query and return one matching row, or None."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def query_as_dicts(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        """Execute query and return results as a list of Python dictionaries."""
        rows = self.fetchall(query, params)
        return [dict(row) for row in rows]


# Global singleton instance for easy import across modules
db = Database()
