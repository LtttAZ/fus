"""Tests for ado_repo_db module."""

import sqlite3
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from azure.devops.v7_0.git.models import GitRepository


@pytest.fixture
def mock_repos():
    """Create mock GitRepository objects."""
    repo1 = Mock(spec=GitRepository)
    repo1.id = "2f3d611a-f012-4b39-b157-8db63f380226"
    repo1.name = "my-repo"

    repo2 = Mock(spec=GitRepository)
    repo2.id = "8a4b722c-e023-5c40-c268-9fc74e7f6e3e"
    repo2.name = "another-repo"

    return [repo1, repo2]


@pytest.fixture
def db_path(tmp_path):
    """Provide a temp DB path and patch get_db_path."""
    path = tmp_path / ".fus" / "ado.db"
    with patch("src.common.ado_repo_db.get_db_path", return_value=path):
        yield path


class TestUpsertAll:
    """Tests for upsert_all function."""

    def test_creates_db_and_table_on_first_call(self, db_path, mock_repos):
        """upsert_all creates DB file and repos table when they don't exist."""
        from src.common.ado_repo_db import upsert_all

        assert not db_path.exists()

        upsert_all(mock_repos)

        assert db_path.exists()

        # Verify table exists and has correct schema
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repos'")
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_inserts_all_repos(self, db_path, mock_repos):
        """upsert_all inserts all provided repositories."""
        from src.common.ado_repo_db import upsert_all

        upsert_all(mock_repos)

        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("SELECT id, name FROM repos ORDER BY name")
            rows = cursor.fetchall()
        finally:
            conn.close()

        assert len(rows) == 2
        assert ("8a4b722c-e023-5c40-c268-9fc74e7f6e3e", "another-repo") in rows
        assert ("2f3d611a-f012-4b39-b157-8db63f380226", "my-repo") in rows

    def test_updates_existing_entries(self, db_path, mock_repos):
        """upsert_all replaces existing entries with new data (upsert behavior)."""
        from src.common.ado_repo_db import upsert_all

        # First insert
        upsert_all(mock_repos)

        # Update repo1 with a new name (same id)
        updated_repo1 = Mock(spec=GitRepository)
        updated_repo1.id = "2f3d611a-f012-4b39-b157-8db63f380226"
        updated_repo1.name = "my-repo-renamed"

        upsert_all([updated_repo1])

        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("SELECT name FROM repos WHERE id = ?", ("2f3d611a-f012-4b39-b157-8db63f380226",))
            row = cursor.fetchone()
        finally:
            conn.close()

        assert row is not None
        assert row[0] == "my-repo-renamed"

    def test_upsert_empty_list(self, db_path):
        """upsert_all with empty list creates DB but inserts nothing."""
        from src.common.ado_repo_db import upsert_all

        upsert_all([])

        assert db_path.exists()

        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM repos")
            count = cursor.fetchone()[0]
        finally:
            conn.close()

        assert count == 0


class TestGetIdByName:
    """Tests for get_id_by_name function."""

    def test_creates_empty_db_if_not_exists(self, db_path):
        """get_id_by_name creates DB and table if they don't exist."""
        from src.common.ado_repo_db import get_id_by_name

        assert not db_path.exists()

        result = get_id_by_name("nonexistent-repo")

        assert db_path.exists()
        assert result is None

    def test_returns_id_for_known_name(self, db_path, mock_repos):
        """get_id_by_name returns the correct ID for a known repo name."""
        from src.common.ado_repo_db import upsert_all, get_id_by_name

        upsert_all(mock_repos)

        result = get_id_by_name("my-repo")

        assert result == "2f3d611a-f012-4b39-b157-8db63f380226"

    def test_returns_none_for_unknown_name(self, db_path, mock_repos):
        """get_id_by_name returns None when repo name is not in DB."""
        from src.common.ado_repo_db import upsert_all, get_id_by_name

        upsert_all(mock_repos)

        result = get_id_by_name("nonexistent-repo")

        assert result is None

    def test_idempotent_initialization(self, db_path):
        """Multiple calls to get_id_by_name without upsert_all work correctly."""
        from src.common.ado_repo_db import get_id_by_name

        # Call multiple times — should not error and return None each time
        result1 = get_id_by_name("some-repo")
        result2 = get_id_by_name("some-repo")
        result3 = get_id_by_name("another-repo")

        assert result1 is None
        assert result2 is None
        assert result3 is None
        assert db_path.exists()
