"""ADO (Azure DevOps) CLI tool."""

import typer
import yaml
from pathlib import Path
from typing import Optional
from platformdirs import user_config_dir

app = typer.Typer(help="Azure DevOps CLI tool")
config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")


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


@config_app.command("set")
def config_set(
    project: Optional[str] = typer.Option(None, "--project", help="Azure DevOps project name"),
    org: Optional[str] = typer.Option(None, "--org", help="Azure DevOps organization name"),
) -> None:
    """Set configuration values."""
    # Collect provided options
    updates = {}
    if project is not None:
        updates["project"] = project
    if org is not None:
        updates["org"] = org

    # Check that at least one option was provided
    if not updates:
        typer.echo("At least one configuration option must be provided")
        raise typer.Exit(code=1)

    # Read existing config and merge
    config_path = get_config_path()
    existing_config = read_config(config_path)
    existing_config.update(updates)

    # Write updated config
    write_config(config_path, existing_config)

    # Display success message
    updates_str = ", ".join(f"{key}={value}" for key, value in updates.items())
    typer.echo(f"Configuration saved: {updates_str}")


if __name__ == "__main__":
    app()
