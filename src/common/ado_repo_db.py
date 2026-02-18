"""SQLite database for caching ADO repository ID/name mappings."""

import sqlite3
from pathlib import Path
from typing import Optional, List
from azure.devops.v7_0.git.models import GitRepository


def get_db_path() -> Path:
    """
    Get the path to the ADO database file.

    Returns:
        Path to ~/.fus/ado.db (cross-platform home directory)
    """
    return Path.home() / ".fus" / "ado.db"


def _ensure_db_exists(db_path: Path) -> None:
    """
    Ensure database directory and table exist.

    Args:
        db_path: Path to database file
    """
    # Create directory if needed
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create table if not exists
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repos (
                id   TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def upsert_all(repos: List[GitRepository]) -> None:
    """
    Insert or replace all repositories in the database.

    Args:
        repos: List of GitRepository objects to cache
    """
    db_path = get_db_path()
    _ensure_db_exists(db_path)

    conn = sqlite3.connect(db_path)
    try:
        for repo in repos:
            conn.execute(
                "INSERT OR REPLACE INTO repos (id, name) VALUES (?, ?)",
                (repo.id, repo.name)
            )
        conn.commit()
    finally:
        conn.close()


def get_id_by_name(repo_name: str) -> Optional[str]:
    """
    Look up repository ID by name.

    Args:
        repo_name: Repository name to look up

    Returns:
        Repository ID (GUID) if found, None otherwise
    """
    db_path = get_db_path()
    _ensure_db_exists(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT id FROM repos WHERE name = ?",
            (repo_name,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()
