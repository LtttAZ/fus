"""Client for interacting with Azure DevOps API using official SDK."""

from typing import Optional, List
from azure.devops.connection import Connection
from azure.devops.v7_0.git.git_client import GitClient
from azure.devops.v7_0.git.models import GitRepository
from msrest.authentication import BasicAuthentication

from src.common.ado_config import AdoConfig
from src.common.ado_exceptions import (
    AdoClientError,
    AdoAuthError,
    AdoNotFoundError,
)


class AdoClient:
    """Client for interacting with Azure DevOps API using official SDK."""

    def __init__(self, config: Optional[AdoConfig] = None):
        """
        Initialize ADO client.

        Args:
            config: AdoConfig instance. If None, loads from default location.
        """
        self.config = config or AdoConfig()
        self._connection = self._create_connection()
        self._git_client = self._connection.clients.get_git_client()

    def _create_connection(self) -> Connection:
        """Create Azure DevOps connection with authentication."""
        # Build organization URL
        org_url = f"{self.config.server}/{self.config.org}"

        # Create credentials with PAT
        credentials = BasicAuthentication('', self.config.pat)

        # Create connection
        connection = Connection(base_url=org_url, creds=credentials)

        return connection

    def list_repos(self, project: Optional[str] = None) -> List[GitRepository]:
        """
        List all repositories in a project.

        Args:
            project: Project name. If None, uses configured project.

        Returns:
            List of GitRepository objects

        Raises:
            AdoClientError: If API request fails
            AdoAuthError: If authentication fails
            AdoNotFoundError: If project not found
        """
        project_name = project or self.config.project

        try:
            repos = self._git_client.get_repositories(project_name)
            return repos
        except Exception as e:
            self._handle_sdk_exception(e)

    def get_repo(self, repo_id: str, project: Optional[str] = None) -> GitRepository:
        """
        Get details of a specific repository.

        Args:
            repo_id: Repository ID or name
            project: Project name. If None, uses configured project.

        Returns:
            GitRepository object

        Raises:
            AdoClientError: If API request fails
            AdoAuthError: If authentication fails
            AdoNotFoundError: If repository not found
        """
        project_name = project or self.config.project

        try:
            repo = self._git_client.get_repository(
                project=project_name,
                repository_id=repo_id
            )
            return repo
        except Exception as e:
            self._handle_sdk_exception(e)

    def _handle_sdk_exception(self, exception: Exception) -> None:
        """Convert SDK exceptions to our custom exceptions."""
        error_msg = str(exception)

        if "401" in error_msg or "Unauthorized" in error_msg:
            raise AdoAuthError("Authentication failed. Check your ADO_PAT environment variable.")
        elif "404" in error_msg or "not found" in error_msg.lower():
            raise AdoNotFoundError(f"Resource not found: {error_msg}")
        else:
            raise AdoClientError(f"Azure DevOps API error: {error_msg}")
