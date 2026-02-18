"""SQLite database for caching ADO repository ID/name mappings."""

from pathlib import Path
from typing import Optional, List
from azure.devops.v7_0.git.models import GitRepository
from peewee import Model, TextField, SqliteDatabase


class Repo(Model):
    id = TextField(primary_key=True)
    name = TextField()

    class Meta:
        table_name = "repos"
        # No database — bound per-call via bind_ctx


def get_db_path() -> Path:
    """
    Get the path to the ADO database file.

    Returns:
        Path to ~/.fus/ado.db (cross-platform home directory)
    """
    return Path.home() / ".fus" / "ado.db"


def _open_db() -> SqliteDatabase:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database = SqliteDatabase(str(db_path))
    database.connect()
    with database.bind_ctx([Repo]):
        database.create_tables([Repo], safe=True)
    return database


def upsert_all(repos: List[GitRepository]) -> None:
    """
    Insert or replace all repositories in the database.

    Args:
        repos: List of GitRepository objects to cache
    """
    database = _open_db()
    try:
        with database.bind_ctx([Repo]):
            with database.atomic():
                for repo in repos:
                    Repo.replace(id=repo.id, name=repo.name).execute()
    finally:
        database.close()


def get_id_by_name(repo_name: str) -> Optional[str]:
    """
    Look up repository ID by name.

    Args:
        repo_name: Repository name to look up

    Returns:
        Repository ID (GUID) if found, None otherwise
    """
    database = _open_db()
    try:
        with database.bind_ctx([Repo]):
            result = Repo.get_or_none(Repo.name == repo_name)
            return result.id if result else None
    finally:
        database.close()
