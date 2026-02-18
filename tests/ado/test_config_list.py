"""Integration tests for ado config list command."""

import pytest
import yaml
from pathlib import Path


def get_config_path(config_dir: str) -> Path:
    """Get the path to ado.yaml config file."""
    return Path(config_dir) / "ado.yaml"


def write_config(config_path: Path, config: dict) -> None:
    """Write config dictionary to YAML file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f)


def read_config(config_path: Path) -> dict:
    """Read and parse the YAML config file."""
    if not config_path.exists():
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


class TestConfigListWithFullConfig:
    """Test listing configuration when all values are set."""

    def test_list_all_values_with_default_server(self, runner, mock_config_dir):
        """Test listing config with org and project, server shows default."""
        from src.cli.ado import app

        # Create config with org and project only
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "MyOrganization",
            "project": "MyProject"
        })

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        # Check output format and sorting (alphabetical: org, project, server)
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 3
        assert lines[0] == "org: MyOrganization"
        assert lines[1] == "project: MyProject"
        assert lines[2] == "server: https://dev.azure.com"

    def test_list_all_values_with_configured_server(self, runner, mock_config_dir):
        """Test listing config with all values including explicit server."""
        from src.cli.ado import app

        # Create config with all values
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "MyOrg",
            "project": "MyProj",
            "server": "https://dev.azure.com"
        })

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 3
        assert lines[0] == "org: MyOrg"
        assert lines[1] == "project: MyProj"
        assert lines[2] == "server: https://dev.azure.com"

    def test_list_with_onpremises_server(self, runner, mock_config_dir):
        """Test listing config with on-premises server."""
        from src.cli.ado import app

        # Create config with on-premises server
        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "CompanyOrg",
            "project": "CompanyProject",
            "server": "https://tfs.company.com"
        })

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 3
        assert lines[0] == "org: CompanyOrg"
        assert lines[1] == "project: CompanyProject"
        assert lines[2] == "server: https://tfs.company.com"


class TestConfigListWithPartialConfig:
    """Test listing configuration with only some values set."""

    def test_list_org_only(self, runner, mock_config_dir):
        """Test listing config with only org configured."""
        from src.cli.ado import app

        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {"org": "MyOrg"})

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 2
        assert lines[0] == "org: MyOrg"
        assert lines[1] == "server: https://dev.azure.com"

    def test_list_project_only(self, runner, mock_config_dir):
        """Test listing config with only project configured."""
        from src.cli.ado import app

        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {"project": "MyProject"})

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 2
        assert lines[0] == "project: MyProject"
        assert lines[1] == "server: https://dev.azure.com"

    def test_list_server_only(self, runner, mock_config_dir):
        """Test listing config with only server configured."""
        from src.cli.ado import app

        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {"server": "https://tfs.company.com"})

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 1
        assert lines[0] == "server: https://tfs.company.com"


class TestConfigListWithNoConfig:
    """Test listing configuration when config file doesn't exist."""

    def test_list_no_config_file(self, runner, mock_config_dir):
        """Test listing when config file doesn't exist - shows default server only."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 1
        assert lines[0] == "server: https://dev.azure.com"


class TestConfigListSorting:
    """Test that output is sorted alphabetically."""

    def test_sorting_is_alphabetical(self, runner, mock_config_dir):
        """Test that keys are sorted alphabetically regardless of order in file."""
        from src.cli.ado import app

        # Write config with keys in non-alphabetical order
        config_path = get_config_path(mock_config_dir)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write YAML manually to control order
        with open(config_path, 'w') as f:
            f.write("server: https://tfs.company.com\n")
            f.write("project: MyProject\n")
            f.write("org: MyOrg\n")

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')
        # Should be sorted: org, project, server
        assert len(lines) == 3
        assert lines[0] == "org: MyOrg"
        assert lines[1] == "project: MyProject"
        assert lines[2] == "server: https://tfs.company.com"


class TestConfigListOutputFormat:
    """Test output format."""

    def test_output_format_is_key_colon_space_value(self, runner, mock_config_dir):
        """Test that output format is 'key: value'."""
        from src.cli.ado import app

        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {"org": "TestOrg"})

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')

        # Each line should match format "key: value"
        for line in lines:
            assert ': ' in line
            parts = line.split(': ')
            assert len(parts) == 2
            assert parts[0]  # key is non-empty
            assert parts[1]  # value is non-empty

    def test_values_with_spaces_formatted_correctly(self, runner, mock_config_dir):
        """Test that values containing spaces are formatted correctly."""
        from src.cli.ado import app

        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {
            "org": "My Organization",
            "project": "My Project Name"
        })

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        lines = result.stdout.strip().split('\n')
        assert "org: My Organization" in lines
        assert "project: My Project Name" in lines


class TestConfigListExitCodes:
    """Test exit codes."""

    def test_exit_code_zero_with_config(self, runner, mock_config_dir):
        """Test that exit code is 0 when config exists."""
        from src.cli.ado import app

        config_path = get_config_path(mock_config_dir)
        write_config(config_path, {"org": "MyOrg"})

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0

    def test_exit_code_zero_without_config(self, runner, mock_config_dir):
        """Test that exit code is 0 even when config doesn't exist."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
