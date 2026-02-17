"""Integration tests for ado config set command."""

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


def read_config(config_path: Path) -> dict:
    """Read and parse the YAML config file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


class TestConfigSetSingleOption:
    """Test setting single configuration options."""

    def test_set_project_only(self, runner, mock_config_dir):
        """Test setting only the project configuration."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--project", "MyProject"])

        assert result.exit_code == 0
        assert "Configuration saved: project=MyProject" in result.stdout

        config_path = get_config_path(mock_config_dir)
        assert config_path.exists()

        config = read_config(config_path)
        assert config == {"project": "MyProject"}

    def test_set_org_only(self, runner, mock_config_dir):
        """Test setting only the org configuration."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--org", "MyOrganization"])

        assert result.exit_code == 0
        assert "Configuration saved: org=MyOrganization" in result.stdout

        config_path = get_config_path(mock_config_dir)
        assert config_path.exists()

        config = read_config(config_path)
        assert config == {"org": "MyOrganization"}

    def test_set_server_only(self, runner, mock_config_dir):
        """Test setting only the server configuration."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--server", "https://tfs.company.com"])

        assert result.exit_code == 0
        assert "Configuration saved: server=https://tfs.company.com" in result.stdout

        config_path = get_config_path(mock_config_dir)
        assert config_path.exists()

        config = read_config(config_path)
        assert config == {"server": "https://tfs.company.com"}


class TestConfigSetMultipleOptions:
    """Test setting multiple configuration options."""

    def test_set_project_and_org(self, runner, mock_config_dir):
        """Test setting both project and org configuration."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--project", "MyProject", "--org", "MyOrg"])

        assert result.exit_code == 0
        # Check that both values are in the output (order may vary)
        assert "Configuration saved:" in result.stdout
        assert "project=MyProject" in result.stdout
        assert "org=MyOrg" in result.stdout

        config_path = get_config_path(mock_config_dir)
        assert config_path.exists()

        config = read_config(config_path)
        assert config == {"project": "MyProject", "org": "MyOrg"}

    def test_set_all_options(self, runner, mock_config_dir):
        """Test setting all configuration options at once."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--project", "MyProject", "--org", "MyOrg", "--server", "https://tfs.company.com"])

        assert result.exit_code == 0
        # Check that all values are in the output (order may vary)
        assert "Configuration saved:" in result.stdout
        assert "project=MyProject" in result.stdout
        assert "org=MyOrg" in result.stdout
        assert "server=https://tfs.company.com" in result.stdout

        config_path = get_config_path(mock_config_dir)
        assert config_path.exists()

        config = read_config(config_path)
        assert config == {"project": "MyProject", "org": "MyOrg", "server": "https://tfs.company.com"}


class TestConfigSetMerging:
    """Test merging with existing configuration."""

    def test_update_preserves_existing_values(self, runner, mock_config_dir):
        """Test that updating one value preserves other existing values."""
        from src.cli.ado import app

        # First, set both project and org
        runner.invoke(app, ["config", "set", "--project", "Project1", "--org", "Org1"])

        # Then update only project
        result = runner.invoke(app, ["config", "set", "--project", "Project2"])

        assert result.exit_code == 0
        assert "Configuration saved: project=Project2" in result.stdout

        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)

        # Org should still be preserved
        assert config == {"project": "Project2", "org": "Org1"}

    def test_update_multiple_preserves_others(self, runner, mock_config_dir):
        """Test updating multiple values while preserving others."""
        from src.cli.ado import app

        # Set initial config with project and org
        config_path = get_config_path(mock_config_dir)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        initial_config = {"project": "OldProject", "org": "OldOrg", "other": "preserved"}
        with open(config_path, 'w') as f:
            yaml.dump(initial_config, f)

        # Update project and org
        result = runner.invoke(app, ["config", "set", "--project", "NewProject", "--org", "NewOrg"])

        assert result.exit_code == 0

        config = read_config(config_path)
        # Should update project and org, but preserve 'other'
        assert config == {"project": "NewProject", "org": "NewOrg", "other": "preserved"}

    def test_update_preserves_server(self, runner, mock_config_dir):
        """Test that updating project/org preserves server."""
        from src.cli.ado import app

        # First, set all three values
        runner.invoke(app, ["config", "set", "--project", "Project1", "--org", "Org1", "--server", "https://tfs.company.com"])

        # Then update only project
        result = runner.invoke(app, ["config", "set", "--project", "Project2"])

        assert result.exit_code == 0
        assert "Configuration saved: project=Project2" in result.stdout

        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)

        # Server and org should still be preserved
        assert config == {"project": "Project2", "org": "Org1", "server": "https://tfs.company.com"}


class TestConfigSetDirectoryCreation:
    """Test that config directory is created if it doesn't exist."""

    def test_creates_config_directory(self, runner, temp_config_dir):
        """Test that the config directory is created if it doesn't exist."""
        from src.cli.ado import app

        # Ensure the directory doesn't exist
        config_dir = Path(temp_config_dir) / "fus"
        assert not config_dir.exists()

        with patch('src.common.ado_config.user_config_dir', return_value=str(config_dir)):
            result = runner.invoke(app, ["config", "set", "--project", "MyProject"])

        assert result.exit_code == 0
        assert config_dir.exists()

        config_path = config_dir / "ado.yaml"
        assert config_path.exists()


class TestConfigSetErrors:
    """Test error handling."""

    def test_no_options_provided(self, runner, mock_config_dir):
        """Test that an error is shown when no options are provided."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set"])

        assert result.exit_code == 1
        assert "At least one configuration option must be provided" in result.stdout


class TestConfigSetOutput:
    """Test output messages."""

    def test_success_message_format(self, runner, mock_config_dir):
        """Test that success message follows the correct format."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--project", "TestProject"])

        assert result.exit_code == 0
        assert result.stdout.strip() == "Configuration saved: project=TestProject"

    def test_success_message_multiple_values(self, runner, mock_config_dir):
        """Test success message with multiple values."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--project", "Proj", "--org", "Org"])

        assert result.exit_code == 0
        assert "Configuration saved:" in result.stdout
        # Both values should be in the message
        assert "project=Proj" in result.stdout
        assert "org=Org" in result.stdout


class TestConfigSetRepoOptions:
    """Test repo-specific configuration options."""

    def test_set_repo_columns_only(self, runner, mock_config_dir):
        """Test setting repo columns only."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--repo-columns", "name,url"])

        assert result.exit_code == 0
        assert "Configuration saved: repo.columns=name,url" in result.stdout

        # Verify config file
        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)
        assert "repo" in config
        assert config["repo"]["columns"] == "name,url"

    def test_set_repo_column_names_only(self, runner, mock_config_dir):
        """Test setting repo column names only."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--repo-column-names", "Repository,URL"])

        assert result.exit_code == 0
        assert "Configuration saved: repo.column-names=Repository,URL" in result.stdout

        # Verify config file
        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)
        assert "repo" in config
        assert config["repo"]["column-names"] == "Repository,URL"

    def test_set_repo_columns_and_names(self, runner, mock_config_dir):
        """Test setting both repo columns and column names."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--repo-columns", "name,web_url", "--repo-column-names", "Name,URL"])

        assert result.exit_code == 0
        assert "Configuration saved:" in result.stdout
        assert "repo.columns=name,web_url" in result.stdout
        assert "repo.column-names=Name,URL" in result.stdout

        # Verify config file
        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)
        assert "repo" in config
        assert config["repo"]["columns"] == "name,web_url"
        assert config["repo"]["column-names"] == "Name,URL"

    def test_set_repo_options_with_top_level(self, runner, mock_config_dir):
        """Test setting repo options along with top-level config."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--org", "MyOrg", "--repo-columns", "id,name"])

        assert result.exit_code == 0
        assert "Configuration saved:" in result.stdout
        assert "org=MyOrg" in result.stdout
        assert "repo.columns=id,name" in result.stdout

        # Verify config file
        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)
        assert config["org"] == "MyOrg"
        assert config["repo"]["columns"] == "id,name"

    def test_update_repo_columns_preserves_column_names(self, runner, mock_config_dir):
        """Test updating repo columns preserves existing column names."""
        from src.cli.ado import app

        # Set initial config
        config_path = get_config_path(mock_config_dir)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        initial_config = {
            "org": "TestOrg",
            "repo": {
                "columns": "name,id",
                "column-names": "Name,ID"
            }
        }
        with open(config_path, 'w') as f:
            yaml.dump(initial_config, f)

        # Update only columns
        result = runner.invoke(app, ["config", "set", "--repo-columns", "name,url"])

        assert result.exit_code == 0

        # Verify column names are preserved
        config = read_config(config_path)
        assert config["repo"]["columns"] == "name,url"
        assert config["repo"]["column-names"] == "Name,ID"  # Preserved

    def test_set_repo_open_true(self, runner, mock_config_dir):
        """Test setting repo.open to true."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--repo.open=true"])

        assert result.exit_code == 0
        assert "Configuration saved: repo.open=true" in result.stdout

        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)
        assert config["repo"]["open"] is True

    def test_set_repo_open_false(self, runner, mock_config_dir):
        """Test setting repo.open to false."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--repo.open=false"])

        assert result.exit_code == 0
        assert "Configuration saved: repo.open=false" in result.stdout

        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)
        assert config["repo"]["open"] is False

    def test_set_repo_open_invalid_value(self, runner, mock_config_dir):
        """Test that invalid value for repo.open raises error."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "set", "--repo.open=yes"])

        assert result.exit_code == 1
        assert "Error: --repo.open must be 'true' or 'false'" in result.stdout

