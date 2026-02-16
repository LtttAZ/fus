"""Unit tests for AdoClient."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from azure.devops.v7_0.git.models import GitRepository, TeamProjectReference

from src.common.ado_client import AdoClient
from src.common.ado_exceptions import AdoClientError, AdoAuthError, AdoNotFoundError


@pytest.fixture
def mock_config():
    """Create a mock AdoConfig."""
    config = Mock()
    config.server = "https://dev.azure.com"
    config.org = "TestOrg"
    config.project = "TestProject"
    config.pat = "test-pat-token"
    return config


@pytest.fixture
def mock_git_repository():
    """Create a mock GitRepository object."""
    repo = Mock(spec=GitRepository)
    repo.id = "repo-123"
    repo.name = "test-repo"
    repo.url = "https://dev.azure.com/TestOrg/_apis/git/repositories/repo-123"
    repo.remote_url = "https://dev.azure.com/TestOrg/TestProject/_git/test-repo"
    repo.ssh_url = "git@ssh.dev.azure.com:v3/TestOrg/TestProject/test-repo"
    repo.web_url = "https://dev.azure.com/TestOrg/TestProject/_git/test-repo"
    repo.default_branch = "refs/heads/main"

    # Mock project
    project = Mock(spec=TeamProjectReference)
    project.id = "project-456"
    project.name = "TestProject"
    repo.project = project

    return repo


class TestAdoClientInitialization:
    """Test AdoClient initialization."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_init_with_default_config(self, mock_read_config, mock_connection):
        """Test initialization with default config."""
        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        client = AdoClient()

        assert client.config is not None
        mock_connection.assert_called_once()

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_init_with_custom_config(self, mock_connection, mock_config):
        """Test initialization with custom config."""
        client = AdoClient(config=mock_config)

        assert client.config == mock_config
        mock_connection.assert_called_once()

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_connection_created_with_correct_url(self, mock_connection, mock_config):
        """Test that connection is created with correct organization URL."""
        from msrest.authentication import BasicAuthentication

        client = AdoClient(config=mock_config)

        # Verify connection was called with correct org URL
        expected_url = f"{mock_config.server}/{mock_config.org}"
        call_args = mock_connection.call_args
        assert call_args[1]["base_url"] == expected_url

        # Verify credentials are BasicAuthentication with PAT
        creds = call_args[1]["creds"]
        assert isinstance(creds, BasicAuthentication)


class TestAdoClientListRepos:
    """Test list_repos method."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_list_repos_success(self, mock_connection, mock_config, mock_git_repository):
        """Test successful repository listing."""
        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = [mock_git_repository]

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Test
        client = AdoClient(config=mock_config)
        repos = client.list_repos()

        # Verify
        assert len(repos) == 1
        assert repos[0].name == "test-repo"
        assert repos[0].id == "repo-123"
        mock_git_client.get_repositories.assert_called_once_with("TestProject")

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_list_repos_with_custom_project(self, mock_connection, mock_config, mock_git_repository):
        """Test listing repos with custom project parameter."""
        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = [mock_git_repository]

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Test
        client = AdoClient(config=mock_config)
        repos = client.list_repos(project="CustomProject")

        # Verify
        mock_git_client.get_repositories.assert_called_once_with("CustomProject")

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_list_repos_empty_list(self, mock_connection, mock_config):
        """Test listing repos returns empty list when no repos exist."""
        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = []

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Test
        client = AdoClient(config=mock_config)
        repos = client.list_repos()

        # Verify
        assert repos == []

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_list_repos_auth_error(self, mock_connection, mock_config):
        """Test authentication error is properly handled."""
        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.side_effect = Exception("401 Unauthorized")

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Test
        client = AdoClient(config=mock_config)

        with pytest.raises(AdoAuthError) as exc_info:
            client.list_repos()

        assert "Authentication failed" in str(exc_info.value)
        assert "ADO_PAT" in str(exc_info.value)

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_list_repos_not_found(self, mock_connection, mock_config):
        """Test project not found error is properly handled."""
        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.side_effect = Exception("404 Project not found")

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Test
        client = AdoClient(config=mock_config)

        with pytest.raises(AdoNotFoundError) as exc_info:
            client.list_repos()

        assert "not found" in str(exc_info.value).lower()

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_list_repos_generic_error(self, mock_connection, mock_config):
        """Test generic API error is properly handled."""
        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.side_effect = Exception("500 Internal Server Error")

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Test
        client = AdoClient(config=mock_config)

        with pytest.raises(AdoClientError) as exc_info:
            client.list_repos()

        assert "Azure DevOps API error" in str(exc_info.value)


class TestAdoClientGetRepo:
    """Test get_repo method."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_get_repo_success(self, mock_connection, mock_config, mock_git_repository):
        """Test successful get repository."""
        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repository.return_value = mock_git_repository

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Test
        client = AdoClient(config=mock_config)
        repo = client.get_repo("test-repo")

        # Verify
        assert repo.name == "test-repo"
        assert repo.id == "repo-123"
        mock_git_client.get_repository.assert_called_once_with(
            project="TestProject",
            repository_id="test-repo"
        )

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_get_repo_with_custom_project(self, mock_connection, mock_config, mock_git_repository):
        """Test get repo with custom project parameter."""
        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repository.return_value = mock_git_repository

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Test
        client = AdoClient(config=mock_config)
        repo = client.get_repo("test-repo", project="CustomProject")

        # Verify
        mock_git_client.get_repository.assert_called_once_with(
            project="CustomProject",
            repository_id="test-repo"
        )

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_get_repo_not_found(self, mock_connection, mock_config):
        """Test repository not found error is properly handled."""
        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repository.side_effect = Exception("Repository not found")

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Test
        client = AdoClient(config=mock_config)

        with pytest.raises(AdoNotFoundError):
            client.get_repo("nonexistent-repo")


class TestAdoConfigPAT:
    """Test AdoConfig PAT property."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    def test_pat_from_environment(self):
        """Test PAT is read from environment variable."""
        from src.common.ado_config import AdoConfig

        config = AdoConfig()
        assert config.pat == "test-token"

    @patch.dict(os.environ, {}, clear=True)
    def test_pat_missing_raises_error(self):
        """Test error when ADO_PAT environment variable is not set."""
        from src.common.ado_config import AdoConfig
        import typer

        config = AdoConfig()

        with pytest.raises(typer.Exit) as exc_info:
            _ = config.pat

        assert exc_info.value.exit_code == 1
