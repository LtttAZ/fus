"""Azure DevOps utility functions."""

import json
import re
from typing import Optional, Any
from urllib.parse import urlparse


def parse_ado_remote_url(remote_url: str) -> Optional[tuple[str, str, str, str]]:
    """
    Parse Azure DevOps remote URL to extract server, org, project, and repo.

    Args:
        remote_url: Git remote URL

    Returns:
        Tuple of (server, org, project, repo) if valid ADO URL, None otherwise.
        server will be "https://dev.azure.com" for cloud, or the actual server for on-premises.
    """
    # HTTPS format: https://dev.azure.com/{org}/{project}/_git/{repo}
    # HTTPS with username: https://{org}@dev.azure.com/{org}/{project}/_git/{repo}
    https_pattern = r'https://(?:[^@]+@)?([^/]+)/([^/]+)/([^/]+)/_git/([^/\s]+?)(?:\.git)?$'
    match = re.match(https_pattern, remote_url)
    if match:
        server = match.group(1)
        org = match.group(2)
        project = match.group(3)
        repo = match.group(4)

        # Normalize server URL
        if 'dev.azure.com' in server:
            server = 'https://dev.azure.com'
        else:
            server = f'https://{server}'

        return (server, org, project, repo)

    # SSH format: git@ssh.dev.azure.com:v3/{org}/{project}/{repo}
    ssh_pattern = r'git@ssh\.dev\.azure\.com:v3/([^/]+)/([^/]+)/([^/\s]+?)(?:\.git)?$'
    match = re.match(ssh_pattern, remote_url)
    if match:
        org = match.group(1)
        project = match.group(2)
        repo = match.group(3)
        return ('https://dev.azure.com', org, project, repo)

    return None


def build_ado_repo_url(server: str, org: str, project: str, repo: str, branch: Optional[str] = None) -> str:
    """
    Build Azure DevOps repository URL.

    Args:
        server: Server base URL (e.g., "https://dev.azure.com" or on-premises server)
        org: Organization name
        project: Project name
        repo: Repository name
        branch: Optional branch name

    Returns:
        Full Azure DevOps repository URL
    """
    base_url = f"{server}/{org}/{project}/_git/{repo}"

    if branch:
        return f"{base_url}?version=GB{branch}"

    return base_url


def build_ado_workitem_url(server: str, org: str, project: str, workitem_id: int) -> str:
    """
    Build Azure DevOps work item URL.

    Args:
        server: Server base URL (e.g., "https://dev.azure.com" or on-premises server)
        org: Organization name
        project: Project name
        workitem_id: Work item ID

    Returns:
        Full Azure DevOps work item URL
    """
    return f"{server}/{org}/{project}/_workitems/edit/{workitem_id}"


def get_nested_value(obj: Any, field_path: str) -> Any:
    """
    Get nested value from object using dot notation.

    If a nested value is a JSON string, parse it before continuing.

    Args:
        obj: Object to access
        field_path: Dot-separated path (e.g., "project.name")

    Returns:
        The value at the field path

    Raises:
        AttributeError: If field path is invalid
    """
    parts = field_path.split(".")
    current = obj

    for part in parts:
        # Get the attribute
        current = getattr(current, part)

        # If it's a string and we have more parts to traverse, try parsing as JSON
        if isinstance(current, str) and parts.index(part) < len(parts) - 1:
            try:
                current = json.loads(current)
            except (json.JSONDecodeError, TypeError):
                # Not valid JSON or not a string, continue with the object as-is
                pass

    return current
