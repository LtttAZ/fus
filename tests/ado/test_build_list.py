"""Integration tests for ado build list command."""

import os
import pytest
from unittest.mock import Mock, patch, call
from typer.testing import CliRunner
from datetime import datetime


@pytest.fixture
def runner():
    """Create a CliRunner for testing."""
    return CliRunner()


@pytest.fixture
def mock_builds():
    """Create mock Build objects."""
    builds = []

    # First build
    build1 = Mock()
    build1.id = 123
    build1.build_number = "20250218.1"
    build1.status = "completed"
    build1.result = "succeeded"
    build1.definition = Mock()
    build1.definition.name = "CI Pipeline"
    build1.source_branch = "refs/heads/main"
    build1.queue_time = datetime(2025, 2, 18, 10, 0, 0)
    build1.finish_time = datetime(2025, 2, 18, 10, 15, 0)

    # Second build
    build2 = Mock()
    build2.id = 122
    build2.build_number = "20250218.0"
    build2.status = "completed"
    build2.result = "failed"
    build2.definition = Mock()
    build2.definition.name = "CI Pipeline"
    build2.source_branch = "refs/heads/feature-x"
    build2.queue_time = datetime(2025, 2, 18, 9, 0, 0)
    build2.finish_time = datetime(2025, 2, 18, 9, 30, 0)

    # Third build with None finish_time
    build3 = Mock()
    build3.id = 121
    build3.build_number = "20250217.5"
    build3.status = "inProgress"
    build3.result = None
    build3.definition = Mock()
    build3.definition.name = "CD Pipeline"
    build3.source_branch = "refs/heads/develop"
    build3.queue_time = datetime(2025, 2, 17, 15, 0, 0)
    build3.finish_time = None

    builds.extend([build1, build2, build3])
    return builds


class TestBuildListBasic:
    """Test basic build list functionality."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    def test_list_builds_default_columns(
        self, mock_get_id_by_name, mock_read_config, mock_connection, runner, mock_builds
    ):
        """Test listing builds with default columns."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "build": {"open": False}
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks
        mock_build_client = Mock()
        mock_build_client.get_builds.return_value = mock_builds

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"])

        # Verify
        assert result.exit_code == 0
        # Should contain row numbers
        assert "1" in result.stdout
        assert "2" in result.stdout
        assert "3" in result.stdout
        # Should contain default column headers
        assert "Build ID" in result.stdout or "id" in result.stdout
        # Should contain build data
        assert "123" in result.stdout
        assert "122" in result.stdout
        assert "121" in result.stdout
        assert "CI Pipeline" in result.stdout
        assert "main" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    def test_list_builds_cache_miss(
        self, mock_get_id_by_name, mock_read_config, mock_connection, runner
    ):
        """Test error when repo not found in cache."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
        }

        # Setup repo lookup to return None (not in cache)
        mock_get_id_by_name.return_value = None

        # Run command
        result = runner.invoke(app, ["build", "list", "--repo-name", "nonexistent-repo"])

        # Verify error exit
        assert result.exit_code == 1
        assert "nonexistent-repo" in result.stdout
        assert "ado repo list" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    def test_list_builds_with_top(
        self, mock_get_id_by_name, mock_read_config, mock_connection, runner, mock_builds
    ):
        """Test --top option limits number of builds."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "build": {"open": False}
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks
        mock_build_client = Mock()
        mock_build_client.get_builds.return_value = mock_builds[:2]  # Only first 2 builds

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo", "--top", "2"])

        # Verify
        assert result.exit_code == 0
        # Verify get_builds was called with top=2
        mock_build_client.get_builds.assert_called_once()
        call_kwargs = mock_build_client.get_builds.call_args.kwargs
        assert call_kwargs["top"] == 2

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    def test_list_builds_empty_result(
        self, mock_get_id_by_name, mock_read_config, mock_connection, runner
    ):
        """Test behavior when API returns empty list."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "build": {"open": False}
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks
        mock_build_client = Mock()
        mock_build_client.get_builds.return_value = []

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"])

        # Verify
        assert result.exit_code == 0
        # Table should exist but have no rows

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    def test_list_builds_null_finish_time(
        self, mock_get_id_by_name, mock_read_config, mock_connection, runner, mock_builds
    ):
        """Test handling of None finish_time."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "build": {"open": False}
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks
        mock_build_client = Mock()
        mock_build_client.get_builds.return_value = [mock_builds[2]]  # Build with None finish_time

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"])

        # Verify
        assert result.exit_code == 0
        # Should contain the em-dash for None value
        assert "—" in result.stdout or "N/A" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    def test_list_builds_auth_error(
        self, mock_get_id_by_name, mock_read_config, mock_connection, runner
    ):
        """Test handling of authentication errors."""
        from src.cli.ado import app
        from src.common.ado_exceptions import AdoAuthError

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks to raise auth error
        mock_build_client = Mock()
        mock_build_client.get_builds.side_effect = AdoAuthError("Invalid credentials")

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"])

        # Verify error exit
        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    def test_list_builds_client_error(
        self, mock_get_id_by_name, mock_read_config, mock_connection, runner
    ):
        """Test handling of client errors."""
        from src.cli.ado import app
        from src.common.ado_exceptions import AdoClientError

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks to raise client error
        mock_build_client = Mock()
        mock_build_client.get_builds.side_effect = AdoClientError("API error")

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"])

        # Verify error exit
        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestBuildListOpen:
    """Test interactive open functionality."""

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    @patch("webbrowser.open")
    def test_build_list_open_valid_selection(
        self, mock_webbrowser_open, mock_get_id_by_name, mock_read_config, mock_connection, runner, mock_builds
    ):
        """Test opening a build when user selects valid #."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "server": "https://dev.azure.com",
            "build": {"open": True}
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks
        mock_build_client = Mock()
        mock_build_client.get_builds.return_value = mock_builds

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command with input "1" (first build)
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"], input="1\n")

        # Verify
        assert result.exit_code == 0
        # Should have called webbrowser.open with correct URL
        mock_webbrowser_open.assert_called_once()
        called_url = mock_webbrowser_open.call_args[0][0]
        assert "buildId=123" in called_url

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    @patch("webbrowser.open")
    def test_build_list_open_skip(
        self, mock_webbrowser_open, mock_get_id_by_name, mock_read_config, mock_connection, runner, mock_builds
    ):
        """Test skipping browser open when user presses Enter."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "build": {"open": True}
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks
        mock_build_client = Mock()
        mock_build_client.get_builds.return_value = mock_builds

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command with empty input (just press Enter)
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"], input="\n")

        # Verify
        assert result.exit_code == 0
        # webbrowser.open should NOT have been called
        mock_webbrowser_open.assert_not_called()

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    @patch("webbrowser.open")
    def test_build_list_open_invalid_index(
        self, mock_webbrowser_open, mock_get_id_by_name, mock_read_config, mock_connection, runner, mock_builds
    ):
        """Test error on invalid build selection."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "build": {"open": True}
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks
        mock_build_client = Mock()
        mock_build_client.get_builds.return_value = mock_builds

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command with invalid index (too high)
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"], input="999\n")

        # Verify
        assert result.exit_code == 0  # Command exits successfully
        assert "Invalid selection" in result.stdout
        mock_webbrowser_open.assert_not_called()

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    @patch("webbrowser.open")
    def test_build_list_open_non_integer_input(
        self, mock_webbrowser_open, mock_get_id_by_name, mock_read_config, mock_connection, runner, mock_builds
    ):
        """Test error on non-integer input."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "build": {"open": True}
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks
        mock_build_client = Mock()
        mock_build_client.get_builds.return_value = mock_builds

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command with non-integer input
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"], input="abc\n")

        # Verify
        assert result.exit_code == 0  # Command exits successfully
        assert "Invalid input" in result.stdout
        mock_webbrowser_open.assert_not_called()

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    @patch("src.common.ado_client.Connection")
    @patch("src.common.ado_config.read_config")
    @patch("src.common.ado_repo_db.get_id_by_name")
    @patch("webbrowser.open")
    def test_build_list_open_disabled(
        self, mock_webbrowser_open, mock_get_id_by_name, mock_read_config, mock_connection, runner, mock_builds
    ):
        """Test no prompt when build.open is false."""
        from src.cli.ado import app

        # Setup config
        mock_read_config.return_value = {
            "org": "TestOrg",
            "project": "TestProject",
            "build": {"open": False}
        }

        # Setup repo lookup
        mock_get_id_by_name.return_value = "repo-123"

        # Setup mocks
        mock_build_client = Mock()
        mock_build_client.get_builds.return_value = mock_builds

        mock_conn_instance = Mock()
        mock_conn_instance.clients.get_build_client.return_value = mock_build_client
        mock_connection.return_value = mock_conn_instance

        # Run command without input (no prompt should be shown)
        result = runner.invoke(app, ["build", "list", "--repo-name", "test-repo"])

        # Verify
        assert result.exit_code == 0
        mock_webbrowser_open.assert_not_called()
