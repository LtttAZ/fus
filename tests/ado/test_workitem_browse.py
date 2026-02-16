"""Integration tests for ado workitem browse command."""

import pytest
import yaml
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch
import tempfile
import shutil


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def runner():
    """Create a CliRunner for testing."""
    return CliRunner()


@pytest.fixture
def mock_config_dir(temp_config_dir):
    """Mock platformdirs.user_config_dir to return temp directory."""
    with patch('src.common.ado_config.user_config_dir', return_value=temp_config_dir):
        yield temp_config_dir


def get_config_path(config_dir: str) -> Path:
    """Get the path to ado.yaml config file."""
    return Path(config_dir) / "ado.yaml"


def write_config(config_path: Path, config: dict) -> None:
    """Write config dictionary to YAML file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f)


class TestWorkitemBrowseSuccess:
    """Test successful workitem browse operations."""

    def test_browse_with_full_config(self, runner, mock_config_dir):
        """Test browsing work item with all config values set."""
        from src.cli.ado import app

        # Set up config
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "myorg",
            "project": "myproject",
            "server": "https://dev.azure.com"
        })

        with patch('src.cli.ado.webbrowser.open') as mock_open:
            result = runner.invoke(app, ["workitem", "browse", "--id", "12345"])

            assert result.exit_code == 0
            assert "Opening: https://dev.azure.com/myorg/myproject/_workitems/edit/12345" in result.stdout
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/myproject/_workitems/edit/12345")

    def test_browse_without_server_uses_default(self, runner, mock_config_dir):
        """Test browsing work item without server config uses default."""
        from src.cli.ado import app

        # Set up config without server
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "myorg",
            "project": "myproject"
        })

        with patch('src.cli.ado.webbrowser.open') as mock_open:
            result = runner.invoke(app, ["workitem", "browse", "--id", "67890"])

            assert result.exit_code == 0
            assert "Opening: https://dev.azure.com/myorg/myproject/_workitems/edit/67890" in result.stdout
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/myproject/_workitems/edit/67890")

    def test_browse_with_onpremises_server(self, runner, mock_config_dir):
        """Test browsing work item with on-premises server."""
        from src.cli.ado import app

        # Set up config with on-premises server
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "contoso",
            "project": "MyProject",
            "server": "https://tfs.company.com"
        })

        with patch('src.cli.ado.webbrowser.open') as mock_open:
            result = runner.invoke(app, ["workitem", "browse", "--id", "999"])

            assert result.exit_code == 0
            assert "Opening: https://tfs.company.com/contoso/MyProject/_workitems/edit/999" in result.stdout
            mock_open.assert_called_once_with("https://tfs.company.com/contoso/MyProject/_workitems/edit/999")


class TestWorkitemBrowseAlias:
    """Test wi alias for workitem browse."""

    def test_browse_using_wi_alias(self, runner, mock_config_dir):
        """Test browsing work item using wi alias."""
        from src.cli.ado import app

        # Set up config
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "myorg",
            "project": "myproject"
        })

        with patch('src.cli.ado.webbrowser.open') as mock_open:
            result = runner.invoke(app, ["wi", "browse", "--id", "54321"])

            assert result.exit_code == 0
            assert "Opening: https://dev.azure.com/myorg/myproject/_workitems/edit/54321" in result.stdout
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/myproject/_workitems/edit/54321")


class TestWorkitemBrowseErrors:
    """Test error handling."""

    def test_missing_org_config(self, runner, mock_config_dir):
        """Test error when org is not configured."""
        from src.cli.ado import app

        # Set up config without org
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "project": "myproject"
        })

        result = runner.invoke(app, ["workitem", "browse", "--id", "12345"])

        assert result.exit_code == 1
        assert "Error: Organization not configured" in result.stdout
        assert "ado config set --org <org>" in result.stdout

    def test_missing_project_config(self, runner, mock_config_dir):
        """Test error when project is not configured."""
        from src.cli.ado import app

        # Set up config without project
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "myorg"
        })

        result = runner.invoke(app, ["workitem", "browse", "--id", "12345"])

        assert result.exit_code == 1
        assert "Error: Project not configured" in result.stdout
        assert "ado config set --project <project>" in result.stdout

    def test_missing_both_org_and_project(self, runner, mock_config_dir):
        """Test error when both org and project are not configured."""
        from src.cli.ado import app

        # Set up empty config
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {})

        result = runner.invoke(app, ["workitem", "browse", "--id", "12345"])

        assert result.exit_code == 1
        # Should show error for org first
        assert "Error: Organization not configured" in result.stdout

    def test_no_config_file(self, runner, mock_config_dir):
        """Test error when config file doesn't exist."""
        from src.cli.ado import app

        # Don't create config file
        result = runner.invoke(app, ["workitem", "browse", "--id", "12345"])

        assert result.exit_code == 1
        assert "Error: Organization not configured" in result.stdout

    def test_missing_id_option(self, runner, mock_config_dir):
        """Test error when --id option is not provided."""
        from src.cli.ado import app

        # Set up config
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "myorg",
            "project": "myproject"
        })

        result = runner.invoke(app, ["workitem", "browse"])

        # Typer shows error for missing required option with exit code 2
        assert result.exit_code == 2


class TestWorkitemBrowseEdgeCases:
    """Test edge cases."""

    def test_large_work_item_id(self, runner, mock_config_dir):
        """Test with large work item ID."""
        from src.cli.ado import app

        # Set up config
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "myorg",
            "project": "myproject"
        })

        with patch('src.cli.ado.webbrowser.open') as mock_open:
            result = runner.invoke(app, ["wi", "browse", "--id", "999999999"])

            assert result.exit_code == 0
            assert "Opening: https://dev.azure.com/myorg/myproject/_workitems/edit/999999999" in result.stdout
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/myproject/_workitems/edit/999999999")

    def test_project_name_with_spaces(self, runner, mock_config_dir):
        """Test with project name containing spaces."""
        from src.cli.ado import app

        # Set up config with project name containing spaces
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "myorg",
            "project": "My Project"
        })

        with patch('src.cli.ado.webbrowser.open') as mock_open:
            result = runner.invoke(app, ["wi", "browse", "--id", "123"])

            assert result.exit_code == 0
            # URL should contain the project name as-is (browser will handle encoding)
            assert "Opening: https://dev.azure.com/myorg/My Project/_workitems/edit/123" in result.stdout
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/My Project/_workitems/edit/123")
