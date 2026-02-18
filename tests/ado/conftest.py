"""Pytest configuration for ADO CLI tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        # Use ignore_errors to handle any permission issues during cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def runner():
    """Create a CliRunner for testing."""
    return CliRunner()


@pytest.fixture
def mock_config_dir(temp_config_dir):
    """Mock the config directory for test isolation.

    Patches get_config_path in ado_config module to return temp directory path.
    This ensures all config file access in CLI commands goes to the test temp dir.
    """
    from src.common import ado_config

    def mock_get_config_path():
        return Path(temp_config_dir) / "ado.yaml"

    # Patch get_config_path in the module where it's defined
    with patch.object(ado_config, 'get_config_path', mock_get_config_path):
        yield temp_config_dir


