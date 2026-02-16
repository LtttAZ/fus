"""Git utility functions."""

import subprocess
from pathlib import Path
from typing import Optional


def is_git_repository(directory: Optional[Path] = None) -> bool:
    """
    Check if the directory is within a git repository.

    Args:
        directory: Directory to check. Defaults to current working directory.

    Returns:
        True if the directory is within a git repository, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        # git command not found
        return False


def get_remote_url(remote_name: str = "origin", directory: Optional[Path] = None) -> Optional[str]:
    """
    Get the URL of a git remote.

    Args:
        remote_name: Name of the remote. Defaults to "origin".
        directory: Directory of the git repository. Defaults to current working directory.

    Returns:
        The remote URL if found, None otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", remote_name],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except FileNotFoundError:
        # git command not found
        return None


def get_current_branch(directory: Optional[Path] = None) -> Optional[str]:
    """
    Get the current git branch name.

    Args:
        directory: Directory of the git repository. Defaults to current working directory.

    Returns:
        The current branch name if found, None otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except FileNotFoundError:
        # git command not found
        return None
