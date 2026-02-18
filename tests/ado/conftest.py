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
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def runner():
    """Create a CliRunner for testing."""
    return CliRunner()


@pytest.fixture
def mock_config_dir(temp_config_dir):
    """Mock the config directory for test isolation.

    Patches both:
    - src.common.ado_config.user_config_dir: affects get_config_path() internally,
      which is used by AdoConfig class and any internal calls within ado_config module
    - src.cli.ado.get_config_path: affects CLI commands that call get_config_path()
      via the name imported into ado.py at module load time

    Both patches are needed because ado.py does 'from ado_config import get_config_path',
    capturing a direct reference that is NOT affected by patching ado_config.get_config_path.
    """
    config_path = Path(temp_config_dir) / "ado.yaml"

    def mock_get_config_path():
        return config_path

    with patch('src.common.ado_config.user_config_dir', return_value=temp_config_dir), \
         patch('src.cli.ado.get_config_path', side_effect=mock_get_config_path):
        yield temp_config_dir
