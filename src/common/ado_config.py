"""ADO configuration management."""

import os
import yaml
import typer
from pathlib import Path
from platformdirs import user_config_dir


def get_config_path() -> Path:
    """Get the path to the ado.yaml config file."""
    config_dir = Path(user_config_dir("fus"))
    return config_dir / "ado.yaml"


def read_config(config_path: Path) -> dict:
    """Read and parse the YAML config file."""
    if not config_path.exists():
        return {}

    with open(config_path, 'r') as f:
        content = yaml.safe_load(f)
        return content if content is not None else {}


def write_config(config_path: Path, config: dict) -> None:
    """Write config dictionary to YAML file."""
    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        yaml.dump(config, f)


class AdoConfig:
    """ADO configuration with validation and error handling."""

    def __init__(self):
        """Load configuration from file."""
        self.config_path = get_config_path()
        self._data = read_config(self.config_path)

    @property
    def server(self) -> str:
        """Get server URL, defaults to Azure DevOps cloud."""
        return self._data.get("server", "https://dev.azure.com")

    @property
    def org(self) -> str:
        """Get organization name, exits with error if not configured."""
        value = self._data.get("org")
        if not value:
            typer.echo("Error: Organization not configured. Use 'ado config set --org <org>' to set it.")
            raise typer.Exit(code=1)
        return value

    @property
    def project(self) -> str:
        """Get project name, exits with error if not configured."""
        value = self._data.get("project")
        if not value:
            typer.echo("Error: Project not configured. Use 'ado config set --project <project>' to set it.")
            raise typer.Exit(code=1)
        return value

    @property
    def pat(self) -> str:
        """Get Personal Access Token from environment variable, exits with error if not set."""
        value = os.getenv("ADO_PAT")
        if not value:
            typer.echo("Error: ADO_PAT environment variable not set.")
            typer.echo("Set it with: export ADO_PAT='your-personal-access-token'")
            raise typer.Exit(code=1)
        return value
