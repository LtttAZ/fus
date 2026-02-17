"""ADO configuration management."""

import os
import yaml
import typer
from pathlib import Path
from platformdirs import user_config_dir


# Default fields and column names for repo list
DEFAULT_REPO_FIELDS = ["id", "name"]
DEFAULT_REPO_COLUMN_NAMES = ["repo_id", "repo_name"]


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


class RepoConfig:
    """Repository-specific configuration."""

    def __init__(self, repo_data: dict):
        """
        Initialize repo config.

        Args:
            repo_data: Dictionary containing repo-specific config
        """
        self._data = repo_data

    @property
    def columns(self) -> list[str]:
        """Get configured columns for repo list, returns defaults if not set."""
        value = self._data.get("columns")
        if not value:
            return list(DEFAULT_REPO_FIELDS)  # Return copy to avoid mutation
        return [f.strip() for f in value.split(",")]

    @property
    def column_names(self) -> list[str]:
        """Get configured column names for repo list, returns defaults if not set. Raises error if count mismatches columns."""
        value = self._data.get("column-names")
        columns = self.columns

        if not value:
            # If columns are also default, use DEFAULT_REPO_COLUMN_NAMES; otherwise use field names
            if self._data.get("columns") is None:
                return list(DEFAULT_REPO_COLUMN_NAMES)
            return list(columns)

        names = [n.strip() for n in value.split(",")]
        if len(names) != len(columns):
            typer.echo(
                f"Error: Number of column names ({len(names)}) doesn't match "
                f"number of columns ({len(columns)})."
            )
            raise typer.Exit(code=1)
        return names

    @property
    def open(self) -> bool:
        """Get whether to prompt to open a repository after listing, defaults to True."""
        value = self._data.get("open")
        if value is None:
            return True
        return bool(value)


class AdoConfig:
    """ADO configuration with validation and error handling."""

    def __init__(self):
        """Load configuration from file."""
        self.config_path = get_config_path()
        self._data = read_config(self.config_path)
        self._repo_config = None

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

    @property
    def repo(self) -> RepoConfig:
        """Get repository-specific configuration."""
        if self._repo_config is None:
            repo_data = self._data.get("repo", {})
            self._repo_config = RepoConfig(repo_data)
        return self._repo_config
