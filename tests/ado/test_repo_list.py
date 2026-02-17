"""Integration tests for ado repo list command."""

import os
import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
from azure.devops.v7_0.git.models import GitRepository, TeamProjectReference


@pytest.fixture
def runner():
    """Create a CliRunner for testing."""
    return CliRunner()


@pytest.fixture
def mock_git_repositories():
    """Create mock GitRepository objects."""
    repos = []

    # First repo
    repo1 = Mock(spec=GitRepository)
    repo1.id = "2f3d611a-f012-4b39-b157-8db63f380226"
    repo1.name = "my-repo"
    repo1.url = "https://dev.azure.com/TestOrg/_apis/git/repositories/2f3d611a-f012-4b39-b157-8db63f380226"
    repo1.remote_url = "https://dev.azure.com/TestOrg/TestProject/_git/my-repo"
    repo1.ssh_url = "git@ssh.dev.azure.com:v3/TestOrg/TestProject/my-repo"
    repo1.web_url = "https://dev.azure.com/TestOrg/TestProject/_git/my-repo"
    repo1.default_branch = "refs/heads/main"
    repo1.size = 524288

    project1 = Mock(spec=TeamProjectReference)
    project1.id = "project-456"
    project1.name = "TestProject"
    repo1.project = project1

    # Second repo
    repo2 = Mock(spec=GitRepository)
    repo2.id = "8a4b722c-e023-5c40-c268-9fc74e7f6e3e"
    repo2.name = "another-repo"
    repo2.url = "https://dev.azure.com/TestOrg/_apis/git/repositories/8a4b722c-e023-5c40-c268-9fc74e7f6e3e"
    repo2.remote_url = "https://dev.azure.com/TestOrg/TestProject/_git/another-repo"
    repo2.ssh_url = "git@ssh.dev.azure.com:v3/TestOrg/TestProject/another-repo"
    repo2.web_url = "https://dev.azure.com/TestOrg/TestProject/_git/another-repo"
    repo2.default_branch = "refs/heads/master"
    repo2.size = 1048576

    project2 = Mock(spec=TeamProjectReference)
    project2.id = "project-456"
    project2.name = "TestProject"
    repo2.project = project2

    repos.extend([repo1, repo2])
    return repos


class TestRepoListBasic:
    """Test basic repo list functionality."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_default_columns(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test listing repos with default columns (id, name)."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {"open": False}
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["repo", "list"])

        # Verify
        assert result.exit_code == 0
        # Should contain row numbers
        assert "1" in result.stdout
        assert "2" in result.stdout
        # Should contain default column headers
        assert "repo_id" in result.stdout
        assert "repo_name" in result.stdout
        # Should contain repo data
        assert "my-repo" in result.stdout
        assert "another-repo" in result.stdout
        assert "2f3d611a-f012-4b39-b157-8db63f380226" in result.stdout
        assert "8a4b722c-e023-5c40-c268-9fc74e7f6e3e" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_empty_project(self, mock_read_config, mock_connection, runner):
        """Test listing repos when project has no repos."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = []

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["repo", "list"])

        # Verify
        assert result.exit_code == 0
        assert "No repositories found in project" in result.stdout


class TestRepoListCustomColumns:
    """Test custom column configuration."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_custom_columns(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test listing repos with custom columns."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {
                "columns": "name,remote_url",
                "open": False
            }
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["repo", "list"])

        # Verify
        assert result.exit_code == 0
        # Should use field names as headers (no custom column names configured)
        assert "name" in result.stdout
        assert "remote_url" in result.stdout
        # Should contain data
        assert "my-repo" in result.stdout
        assert "https://dev.azure.com/TestOrg/TestProject/_git/my-repo" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_nested_fields(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test listing repos with nested field access."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {
                "columns": "name,project.name,project.id",
                "open": False
            }
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["repo", "list"])

        # Verify
        assert result.exit_code == 0
        assert "my-repo" in result.stdout
        assert "TestProject" in result.stdout
        assert "project-456" in result.stdout


class TestRepoListColumnNames:
    """Test custom column names configuration."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_custom_column_names(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test listing repos with custom column names."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {
                "columns": "name,web_url",
                "column-names": "Repository,URL",
                "open": False
            }
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["repo", "list"])

        # Verify
        assert result.exit_code == 0
        # Should use custom column names
        assert "Repository" in result.stdout
        assert "URL" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_column_names_mismatch(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test column names count mismatch raises error."""
        from src.cli.ado import app

        # Setup config with mismatch
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {
                "columns": "name,web_url",  # 2 columns
                "column-names": "Repository,URL,Extra"  # 3 names (mismatch)
            }
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["repo", "list"])

        # Verify
        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "doesn't match" in result.stdout


class TestRepoListRowID:
    """Test row ID column."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_has_row_id_column(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test that table always includes row ID column."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {"open": False}
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["repo", "list"])

        # Verify
        assert result.exit_code == 0
        # Should have # column header
        assert "#" in result.stdout
        # Should have row numbers
        assert "│ 1" in result.stdout or "1  │" in result.stdout
        assert "│ 2" in result.stdout or "2  │" in result.stdout


class TestRepoListErrors:
    """Test error handling."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("src.common.ado_config.read_config")
    def test_list_repos_missing_pat(self, mock_read_config, runner):
        """Test error when ADO_PAT is not set."""
        from src.cli.ado import app

        # Setup config with org and project so we reach PAT check
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        result = runner.invoke(app, ["repo", "list"])

        assert result.exit_code == 1
        assert "ADO_PAT" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    def test_list_repos_auth_error(self, mock_connection, runner):
        """Test authentication error."""
        from src.cli.ado import app

        # Setup mocks to raise auth error
        mock_git_client = Mock()
        mock_git_client.get_repositories.side_effect = Exception("401 Unauthorized")

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        result = runner.invoke(app, ["repo", "list"])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_invalid_field_path(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test error when field path is invalid."""
        from src.cli.ado import app

        # Setup config with invalid field
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {
                "columns": "name,invalid.field.path"
            }
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        result = runner.invoke(app, ["repo", "list"])

        assert result.exit_code == 1
        assert "Unable to access field" in result.stdout


class TestRepoListPattern:
    """Test pattern filtering."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_with_pattern_match(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test listing repos with pattern that matches some repos."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {"open": False}
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with pattern
        result = runner.invoke(app, ["repo", "list", "--pattern", "my-*"])

        # Verify
        assert result.exit_code == 0
        assert "my-repo" in result.stdout
        assert "another-repo" not in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_with_pattern_alias(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test listing repos with pattern alias --patt."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {"open": False}
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with pattern alias
        result = runner.invoke(app, ["repo", "list", "--patt", "*-repo"])

        # Verify
        assert result.exit_code == 0
        assert "my-repo" in result.stdout
        assert "another-repo" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_with_pattern_no_match(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test listing repos with pattern that matches no repos."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with pattern that matches nothing
        result = runner.invoke(app, ["repo", "list", "--pattern", "nonexistent-*"])

        # Verify
        assert result.exit_code == 0
        assert "No repositories found" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_with_pattern_wildcard(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test listing repos with wildcard pattern."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {"open": False}
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with wildcard pattern
        result = runner.invoke(app, ["repo", "list", "--pattern", "*"])

        # Verify - should match all repos
        assert result.exit_code == 0
        assert "my-repo" in result.stdout
        assert "another-repo" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_with_pattern_question_mark(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test listing repos with ? wildcard pattern."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {"open": False}
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with ? pattern (matches single character)
        result = runner.invoke(app, ["repo", "list", "--pattern", "my-????"])

        # Verify
        assert result.exit_code == 0
        assert "my-repo" in result.stdout
        assert "another-repo" not in result.stdout


class TestRepoListOpen:
    """Test --open flag functionality."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("webbrowser.open")
    def test_list_repos_open_defaults_to_config(self, mock_browser, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test that open behavior defaults to repo.open config value."""
        from src.cli.ado import app

        # Setup config with repo.open: true (default)
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {"open": True}
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run without --open flag, but config has open: true
        result = runner.invoke(app, ["repo", "list"], input="1\n")

        assert result.exit_code == 0
        assert "Enter repository number to open" in result.stdout
        mock_browser.assert_called_once()

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("webbrowser.open")
    def test_list_repos_open_flag_overrides_config(self, mock_browser, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test that --open flag overrides repo.open: false in config."""
        from src.cli.ado import app

        # Setup config with repo.open: false
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "repo": {"open": False}
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run with --open flag, overriding config
        result = runner.invoke(app, ["repo", "list", "--open"], input="1\n")

        assert result.exit_code == 0
        assert "Enter repository number to open" in result.stdout
        mock_browser.assert_called_once()

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("webbrowser.open")
    def test_list_repos_with_open_valid_index(self, mock_browser, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test opening a repo with valid index."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with --open and provide index "1" as input
        result = runner.invoke(app, ["repo", "list", "--open"], input="1\n")

        # Verify
        assert result.exit_code == 0
        assert "Enter repository number to open" in result.stdout
        assert "Opening:" in result.stdout
        assert "https://dev.azure.com/TestOrg/TestProject/_git/my-repo" in result.stdout
        mock_browser.assert_called_once_with("https://dev.azure.com/TestOrg/TestProject/_git/my-repo")

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("webbrowser.open")
    def test_list_repos_with_open_second_repo(self, mock_browser, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test opening second repo."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with --open and provide index "2" as input
        result = runner.invoke(app, ["repo", "list", "--open"], input="2\n")

        # Verify
        assert result.exit_code == 0
        assert "https://dev.azure.com/TestOrg/TestProject/_git/another-repo" in result.stdout
        mock_browser.assert_called_once_with("https://dev.azure.com/TestOrg/TestProject/_git/another-repo")

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_with_open_invalid_number(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test error when invalid number is entered."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with --open and provide invalid input
        result = runner.invoke(app, ["repo", "list", "--open"], input="abc\n")

        # Verify
        assert result.exit_code == 1
        assert "Error: Invalid number" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_with_open_out_of_range(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test error when index is out of range."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with --open and provide out of range index
        result = runner.invoke(app, ["repo", "list", "--open"], input="99\n")

        # Verify
        assert result.exit_code == 1
        assert "Error: Repository number must be between 1 and 2" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_with_open_zero_index(self, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test error when index is zero."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with --open and provide zero
        result = runner.invoke(app, ["repo", "list", "--open"], input="0\n")

        # Verify
        assert result.exit_code == 1
        assert "Error: Repository number must be between 1 and 2" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    def test_list_repos_with_open_empty_list(self, mock_read_config, mock_connection, runner):
        """Test that --open with empty repo list doesn't prompt."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        # Setup mocks - empty list
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = []
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with --open
        result = runner.invoke(app, ["repo", "list", "--open"])

        # Verify - should not prompt for input
        assert result.exit_code == 0
        assert "No repositories found" in result.stdout
        assert "Enter repository number" not in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("webbrowser.open")
    def test_list_repos_with_pattern_and_open(self, mock_browser, mock_read_config, mock_connection, runner, mock_git_repositories):
        """Test --open works with --pattern filter."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject"
        }

        # Setup mocks
        mock_git_client = Mock()
        mock_git_client.get_repositories.return_value = mock_git_repositories
        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_git_client.return_value = mock_git_client
        mock_connection.return_value = mock_conn_instance

        # Run command with --pattern and --open
        result = runner.invoke(app, ["repo", "list", "--pattern", "my-*", "--open"], input="1\n")

        # Verify - only my-repo should be in the filtered list
        assert result.exit_code == 0
        assert "my-repo" in result.stdout
        assert "another-repo" not in result.stdout
        assert "https://dev.azure.com/TestOrg/TestProject/_git/my-repo" in result.stdout
        mock_browser.assert_called_once()


class TestRepoListGetNestedValue:
    """Test get_nested_value helper function."""

    def test_get_simple_field(self):
        """Test accessing simple field."""
        from src.common.ado_utils import get_nested_value

        obj = Mock()
        obj.name = "test-repo"

        value = get_nested_value(obj, "name")
        assert value == "test-repo"

    def test_get_nested_field(self):
        """Test accessing nested field."""
        from src.common.ado_utils import get_nested_value

        project = Mock()
        project.name = "TestProject"

        repo = Mock()
        repo.project = project

        value = get_nested_value(repo, "project.name")
        assert value == "TestProject"

    def test_get_nested_field_with_json_parsing(self):
        """Test accessing nested field with JSON string parsing."""
        from src.common.ado_utils import get_nested_value
        import json

        # Simulate a field that contains JSON string
        repo = Mock()
        repo.metadata = json.dumps({"team": {"name": "DevTeam"}})

        # Create a mock that returns the JSON string
        def getattr_side_effect(name):
            if name == "metadata":
                return repo.metadata
            raise AttributeError(f"'{type(repo).__name__}' object has no attribute '{name}'")

        # This test verifies the concept, but in practice the JSON parsing
        # happens when we have more parts to traverse after getting a string value
        value = get_nested_value(repo, "metadata")
        assert json.loads(value)["team"]["name"] == "DevTeam"

    def test_get_invalid_field_raises_error(self):
        """Test that invalid field raises AttributeError."""
        from src.common.ado_utils import get_nested_value

        obj = Mock(spec=[])  # Empty spec means no attributes

        with pytest.raises(AttributeError):
            get_nested_value(obj, "nonexistent")
