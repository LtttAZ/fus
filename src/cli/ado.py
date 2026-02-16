"""ADO (Azure DevOps) CLI tool."""

import typer
import webbrowser
from typing import Optional
from pathlib import Path
from src.common.ado_config import get_config_path, read_config, write_config
from src.common.git_utils import is_git_repository, get_remote_url, get_current_branch
from src.common.ado_utils import parse_ado_remote_url, build_ado_repo_url, build_ado_workitem_url

app = typer.Typer(help="Azure DevOps CLI tool")
config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")

repo_app = typer.Typer(help="Repository commands")
app.add_typer(repo_app, name="repo")

workitem_app = typer.Typer(help="Work item commands")
app.add_typer(workitem_app, name="workitem")
app.add_typer(workitem_app, name="wi")


@config_app.command("set")
def config_set(
    project: Optional[str] = typer.Option(None, "--project", help="Azure DevOps project name"),
    org: Optional[str] = typer.Option(None, "--org", help="Azure DevOps organization name"),
    server: Optional[str] = typer.Option(None, "--server", help="Azure DevOps server URL"),
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
    # Read config
    config_path = get_config_path()
    config = read_config(config_path)

    # Check for required config values
    server = config.get("server", "https://dev.azure.com")
    org = config.get("org")
    project = config.get("project")

    if not org:
        typer.echo("Error: Organization not configured. Use 'ado config set --org <org>' to set it.")
        raise typer.Exit(code=1)

    if not project:
        typer.echo("Error: Project not configured. Use 'ado config set --project <project>' to set it.")
        raise typer.Exit(code=1)

    # Build URL
    url = build_ado_workitem_url(server, org, project, id)

    # Display and open
    typer.echo(f"Opening: {url}")
    webbrowser.open(url)


if __name__ == "__main__":
    app()
