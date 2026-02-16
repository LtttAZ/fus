"""ADO (Azure DevOps) CLI tool."""

import typer
import webbrowser
import fnmatch
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from src.common.ado_config import get_config_path, read_config, write_config, AdoConfig
from src.common.git_utils import is_git_repository, get_remote_url, get_current_branch
from src.common.ado_utils import parse_ado_remote_url, build_ado_repo_url, build_ado_workitem_url, get_nested_value

app = typer.Typer(help="Azure DevOps CLI tool")
config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")

repo_app = typer.Typer(help="Repository commands")
app.add_typer(repo_app, name="repo")

workitem_app = typer.Typer(help="Work item commands")
app.add_typer(workitem_app, name="workitem")
app.add_typer(workitem_app, name="wi")


def set_nested_value(config: dict, key: str, value: str) -> None:
    """Set a nested value using dot notation."""
    parts = key.split(".")
    current = config

    # Navigate/create nested structure
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        elif not isinstance(current[part], dict):
            # Overwrite non-dict value with dict
            current[part] = {}
        current = current[part]

    # Set the final value
    current[parts[-1]] = value


@config_app.command("set")
def config_set(
    project: Optional[str] = typer.Option(None, "--project", help="Azure DevOps project name"),
    org: Optional[str] = typer.Option(None, "--org", help="Azure DevOps organization name"),
    server: Optional[str] = typer.Option(None, "--server", help="Azure DevOps server URL"),
    repo_columns: Optional[str] = typer.Option(None, "--repo-columns", help="Comma-separated list of repo columns to display"),
    repo_column_names: Optional[str] = typer.Option(None, "--repo-column-names", help="Comma-separated list of repo column display names"),
) -> None:
    """Set configuration values."""
    # Collect provided options
    updates = {}
    if project is not None:
        updates["project"] = project
    if org is not None:
        updates["org"] = org
    if server is not None:
        updates["server"] = server

    # Read existing config
    config_path = get_config_path()
    existing_config = read_config(config_path)

    # Process top-level updates
    existing_config.update(updates)

    # Process nested repo config
    if repo_columns is not None:
        set_nested_value(existing_config, "repo.columns", repo_columns)
        updates["repo.columns"] = repo_columns
    if repo_column_names is not None:
        set_nested_value(existing_config, "repo.column-names", repo_column_names)
        updates["repo.column-names"] = repo_column_names

    # Check that at least one option was provided
    if not updates:
        typer.echo("At least one configuration option must be provided")
        raise typer.Exit(code=1)

    # Write updated config
    write_config(config_path, existing_config)

    # Display success message
    updates_str = ", ".join(f"{key}={value}" for key, value in updates.items())
    typer.echo(f"Configuration saved: {updates_str}")


@config_app.command("list")
def config_list() -> None:
    """List all configuration values."""
    config_path = get_config_path()
    config = read_config(config_path)

    # Apply default for server
    if "server" not in config:
        config["server"] = "https://dev.azure.com"

    # Sort and display
    for key in sorted(config.keys()):
        typer.echo(f"{key}: {config[key]}")


@repo_app.command("browse")
def repo_browse(
    branch: Optional[str] = typer.Option(None, "--branch", help="Branch to browse"),
) -> None:
    """Open the repository in the default web browser."""
    # Check if in git repository
    if not is_git_repository(Path.cwd()):
        typer.echo("Error: Not in a git repository")
        raise typer.Exit(code=1)

    # Get remote URL
    remote_url = get_remote_url("origin", Path.cwd())
    if remote_url is None:
        typer.echo("Error: No remote 'origin' found")
        raise typer.Exit(code=1)

    # Parse ADO URL
    parsed = parse_ado_remote_url(remote_url)
    if parsed is None:
        typer.echo("Error: Remote URL is not a valid Azure DevOps repository URL")
        raise typer.Exit(code=1)

    server, org, project, repo = parsed

    # Determine branch
    branch_to_use = branch
    if branch_to_use is None:
        branch_to_use = get_current_branch(Path.cwd())

    # Build URL
    url = build_ado_repo_url(server, org, project, repo, branch_to_use)

    # Display and open
    typer.echo(f"Opening: {url}")
    webbrowser.open(url)


@workitem_app.command("browse")
def workitem_browse(
    id: int = typer.Option(..., "--id", help="Work item ID"),
) -> None:
    """Open a work item in the default web browser."""
    config = AdoConfig()
    url = build_ado_workitem_url(config.server, config.org, config.project, id)
    typer.echo(f"Opening: {url}")
    webbrowser.open(url)


# Default fields and column names for repo list
DEFAULT_FIELDS = ["id", "name"]
DEFAULT_COLUMN_NAMES = ["repo_id", "repo_name"]


@repo_app.command("list")
def repo_list(
    pattern: Optional[str] = typer.Option(None, "--pattern", "--patt", help="Filter repositories by name using glob pattern"),
) -> None:
    """List all repositories in the project."""
    from src.common.ado_client import AdoClient
    from src.common.ado_exceptions import AdoClientError

    try:
        client = AdoClient()
        repos = client.list_repos()

        # Apply pattern filter if provided
        if pattern:
            repos = [repo for repo in repos if fnmatch.fnmatch(repo.name, pattern)]

        if not repos:
            config = client.config
            typer.echo(f"No repositories found in project '{config.project}'")
            return

        # Get fields configuration
        fields_config = client.config.repo.columns
        if fields_config:
            fields = [f.strip() for f in fields_config.split(",")]
        else:
            fields = DEFAULT_FIELDS

        # Get column names configuration
        column_names_config = client.config.repo.column_names
        if column_names_config:
            column_names = [n.strip() for n in column_names_config.split(",")]
            # Validate count matches
            if len(column_names) != len(fields):
                typer.echo(
                    f"Warning: Number of column names ({len(column_names)}) doesn't match "
                    f"number of columns ({len(fields)}). Using field names as headers."
                )
                column_names = fields
        else:
            # Use defaults if fields are default, otherwise use field names
            if fields == DEFAULT_FIELDS:
                column_names = DEFAULT_COLUMN_NAMES
            else:
                column_names = fields

        # Create rich table
        console = Console(width=200)  # Wider console to avoid truncation
        table = Table(show_header=True, header_style="bold cyan")

        # Add row ID column first
        table.add_column("#", style="dim", width=4)

        # Add data columns
        for column_name in column_names:
            table.add_column(column_name, no_wrap=True)

        # Add rows
        for idx, repo in enumerate(repos, start=1):
            row = [str(idx)]  # Start with row ID
            for field in fields:
                try:
                    value = get_nested_value(repo, field)
                    row.append(str(value) if value is not None else "N/A")
                except (AttributeError, KeyError, IndexError) as e:
                    typer.echo(f"Error: Unable to access field '{field}' on repository object")
                    raise typer.Exit(code=1)
            table.add_row(*row)

        console.print(table)

    except AdoClientError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
