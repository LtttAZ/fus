"""Integration tests for ado config init command."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch


def get_config_path(config_dir: str) -> Path:
    """Helper to get config path in temp directory."""
    return Path(config_dir) / "ado.yaml"


def write_config(config_path: Path, config: dict) -> None:
    """Helper to write config file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f)


def read_config(config_path: Path) -> dict:
    """Helper to read config file."""
    if not config_path.exists():
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


class TestConfigInitSuccess:
    """Test successful config init scenarios."""

    def test_init_creates_config_with_defaults(self, runner, mock_config_dir):
        """Test that init creates config file with default values."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0
        assert "Configuration initialized" in result.stdout

        # Verify config file was created
        config_path = get_config_path(mock_config_dir)
        assert config_path.exists()

        # Verify contents
        config = read_config(config_path)
        assert config["server"] == "https://dev.azure.com"
        assert config["repo"]["columns"] == "id,name"
        assert config["repo"]["column-names"] == "repo_id,repo_name"
        assert config["repo"]["open"] is True

        # Keys without defaults should not be present
        assert "org" not in config
        assert "project" not in config

    def test_init_creates_config_directory(self, runner, temp_config_dir):
        """Test that init creates config directory if it doesn't exist."""
        from src.cli.ado import app

        # Don't use mock_config_dir fixture - we want to test directory creation
        non_existent_dir = Path(temp_config_dir) / "subdir"
        assert not non_existent_dir.exists()

        with patch('src.common.ado_config.user_config_dir', return_value=str(non_existent_dir)):
            result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0
        assert non_existent_dir.exists()
        assert (non_existent_dir / "ado.yaml").exists()

    def test_init_output_message(self, runner, mock_config_dir):
        """Test that init displays success message with config path."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0
        assert "Configuration initialized" in result.stdout
        assert str(get_config_path(mock_config_dir)) in result.stdout


class TestConfigInitErrors:
    """Test config init error scenarios."""

    def test_init_fails_if_config_exists(self, runner, mock_config_dir):
        """Test that init fails if config file already exists."""
        from src.cli.ado import app

        # Create existing config
        config_path = get_config_path(mock_config_dir)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump({"org": "ExistingOrg"}, f)

        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 1
        assert "Error: Configuration file already exists" in result.stdout
        assert str(config_path) in result.stdout

        # Verify existing config was not modified
        config = read_config(config_path)
        assert config == {"org": "ExistingOrg"}


class TestConfigInitStructure:
    """Test the structure of the created config file."""

    def test_init_creates_nested_repo_structure(self, runner, mock_config_dir):
        """Test that repo config is properly nested."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0

        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)

        # Verify nested structure
        assert "repo" in config
        assert isinstance(config["repo"], dict)
        assert "columns" in config["repo"]
        assert "column-names" in config["repo"]
        assert "open" in config["repo"]

    def test_init_only_includes_keys_with_defaults(self, runner, mock_config_dir):
        """Test that only keys with defaults are written."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0

        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)

        # Should have exactly these top-level keys
        assert set(config.keys()) == {"server", "repo", "build"}

        # Should have exactly these repo keys
        assert set(config["repo"].keys()) == {"columns", "column-names", "open"}

        # Should have exactly these build keys
        assert set(config["build"].keys()) == {"columns", "column-names", "open"}

    def test_init_uses_correct_default_values(self, runner, mock_config_dir):
        """Test that all default values are correct."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0

        config_path = get_config_path(mock_config_dir)
        config = read_config(config_path)

        # Verify each default value matches what's documented
        assert config["server"] == "https://dev.azure.com"
        assert config["repo"]["columns"] == "id,name"
        assert config["repo"]["column-names"] == "repo_id,repo_name"
        assert config["repo"]["open"] is True  # Boolean, not string


class TestConfigInitExitCodes:
    """Test exit codes for config init."""

    def test_init_exits_zero_on_success(self, runner, mock_config_dir):
        """Test exit code 0 on successful init."""
        from src.cli.ado import app

        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0

    def test_init_exits_one_on_existing_config(self, runner, mock_config_dir):
        """Test exit code 1 when config already exists."""
        from src.cli.ado import app

        # Create existing config
        config_path = get_config_path(mock_config_dir)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.touch()

        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 1
