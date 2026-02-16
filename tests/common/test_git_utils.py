"""Tests for git utility functions."""

import pytest
import tempfile
import subprocess
from pathlib import Path
from src.common.git_utils import is_git_repository, get_remote_url, get_current_branch


class TestIsGitRepository:
    """Test is_git_repository function."""

    def test_returns_true_in_git_repository(self):
        """Test that it returns True when in a git repository."""
        # Use the current project directory which is a git repo
        result = is_git_repository(Path.cwd())
        assert result is True

    def test_returns_true_in_nested_directory(self):
        """Test that it returns True even in a nested directory of a git repo."""
        # Create a nested path within the current git repo
        nested_dir = Path.cwd() / "src" / "common"
        result = is_git_repository(nested_dir)
        assert result is True

    def test_returns_false_in_non_git_directory(self):
        """Test that it returns False when not in a git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = is_git_repository(Path(temp_dir))
            assert result is False

    def test_returns_false_when_git_not_available(self, monkeypatch):
        """Test that it returns False when git command is not available."""
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("git not found")

        monkeypatch.setattr(subprocess, "run", mock_run)
        result = is_git_repository()
        assert result is False


class TestGetRemoteUrl:
    """Test get_remote_url function."""

    def test_returns_origin_remote_url(self):
        """Test that it returns the origin remote URL if it exists."""
        result = get_remote_url("origin", Path.cwd())
        # Should return a URL if origin exists, or None if it doesn't
        # We can't guarantee origin exists, so just verify the return type
        assert result is None or isinstance(result, str)
        if result is not None:
            assert len(result) > 0

    def test_returns_none_for_nonexistent_remote(self):
        """Test that it returns None for a remote that doesn't exist."""
        result = get_remote_url("nonexistent-remote", Path.cwd())
        assert result is None

    def test_returns_none_in_non_git_directory(self):
        """Test that it returns None when not in a git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_remote_url("origin", Path(temp_dir))
            assert result is None

    def test_returns_none_when_git_not_available(self, monkeypatch):
        """Test that it returns None when git command is not available."""
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("git not found")

        monkeypatch.setattr(subprocess, "run", mock_run)
        result = get_remote_url()
        assert result is None


class TestGetCurrentBranch:
    """Test get_current_branch function."""

    def test_returns_current_branch_name(self):
        """Test that it returns the current branch name."""
        result = get_current_branch(Path.cwd())
        # Should return a branch name
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_none_in_non_git_directory(self):
        """Test that it returns None when not in a git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_current_branch(Path(temp_dir))
            assert result is None

    def test_returns_none_when_git_not_available(self, monkeypatch):
        """Test that it returns None when git command is not available."""
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("git not found")

        monkeypatch.setattr(subprocess, "run", mock_run)
        result = get_current_branch()
        assert result is None
