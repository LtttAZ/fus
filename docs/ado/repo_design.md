# ADO Repo Commands - Design Document

## Overview

The `ado repo` commands provide operations for Azure DevOps repositories. These commands include:
- **browse**: Opens repository in browser using git remote URL (no API required)
- **list**: Lists all repositories in a project using Azure DevOps API (requires ADO_PAT)

## Commands

### repo browse

**Purpose**: Open the current git repository in the default web browser.

**Command**: `ado repo browse`

**Options**:
- `--branch` (optional): Branch name to browse. If not provided, uses the current git branch.

**Behavior**:
1. Verifies current directory is a git repository
2. Retrieves the 'origin' remote URL
3. Parses the remote URL to extract server, org, project, and repo
4. Determines branch (from `--branch` option or current branch)
5. Constructs Azure DevOps URL and opens in browser

**Exit Codes**:
- `0`: Success
- `1`: Error (not in git repo, no remote, invalid URL, etc.)

**Example Usage**:
```bash
ado repo browse                    # Browse current branch
ado repo browse --branch develop   # Browse specific branch
```

### repo list

**Purpose**: List all repositories in the configured Azure DevOps project.

**Command**: `ado repo list`

**Options**: None

**Requirements**:
- Configuration: `org`, `project` must be set in `~/.fus/ado.yaml`
- Environment: `ADO_PAT` environment variable must be set

**Behavior**:
1. Loads configuration from `~/.fus/ado.yaml` (org, project, server)
2. Reads PAT from `ADO_PAT` environment variable
3. Creates AdoClient connection to Azure DevOps API
4. Retrieves list of repositories in the project
5. Displays repository information in a table format

**Exit Codes**:
- `0`: Success
- `1`: Error (config missing, PAT not set, authentication failed, etc.)

**Output Format**:

Display repositories in a formatted table using `rich`:

```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Name         ┃ ID                                   ┃ URL                                                           ┃ Default Branch   ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ my-repo      │ 2f3d611a-f012-4b39-b157-8db63f380226 │ https://dev.azure.com/myorg/myproject/_git/my-repo            │ refs/heads/main  │
│ another-repo │ 8a4b722c-e023-5c40-c268-9fc74e7f6e3e │ https://dev.azure.com/myorg/myproject/_git/another-repo       │ refs/heads/master│
└──────────────┴──────────────────────────────────────┴───────────────────────────────────────────────────────────────┴──────────────────┘
```

**Alternative:** With `--simple` flag (optional future enhancement), use simple text output:
```
my-repo
  ID: 2f3d611a-f012-4b39-b157-8db63f380226
  URL: https://dev.azure.com/myorg/myproject/_git/my-repo
  Default Branch: refs/heads/main

another-repo
  ID: 8a4b722c-e023-5c40-c268-9fc74e7f6e3e
  URL: https://dev.azure.com/myorg/myproject/_git/another-repo
  Default Branch: refs/heads/master
```

**Empty Project Output**:
```
No repositories found in project 'MyProject'
```

**Example Usage**:
```bash
# Configure org and project first
ado config set --org myorg --project myproject

# Set PAT
export ADO_PAT="your-personal-access-token"

# List repositories
ado repo list
```

**Error Handling**:

**Organization Not Configured**:
- Message: `Error: Organization not configured. Use 'ado config set --org <org>' to set it.`
- Exit Code: 1

**Project Not Configured**:
- Message: `Error: Project not configured. Use 'ado config set --project <project>' to set it.`
- Exit Code: 1

**PAT Not Set**:
- Message:
  ```
  Error: ADO_PAT environment variable not set.
  Set it with: export ADO_PAT='your-personal-access-token'
  ```
- Exit Code: 1

**Authentication Failed**:
- Message: `Error: Authentication failed. Check your ADO_PAT environment variable.`
- Exit Code: 1

**Project Not Found**:
- Message: `Error: Resource not found: ...`
- Exit Code: 1

**API Error**:
- Message: `Error: Azure DevOps API error: {error_message}`
- Exit Code: 1

**Implementation Notes**:

**Dependencies**:
- `src.common.ado_client`: For `AdoClient`
- `src.common.ado_exceptions`: For `AdoClientError`, `AdoAuthError`, `AdoNotFoundError`
- `src.common.ado_config`: For `AdoConfig`
- `rich`: For table formatting and pretty output

**Implementation Pattern**:
```python
from rich.console import Console
from rich.table import Table

@repo_app.command("list")
def repo_list() -> None:
    """List all repositories in the project."""
    from src.common.ado_client import AdoClient
    from src.common.ado_exceptions import AdoClientError

    try:
        client = AdoClient()
        repos = client.list_repos()

        if not repos:
            config = client.config
            typer.echo(f"No repositories found in project '{config.project}'")
            return

        # Create rich table
        console = Console()
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Name", style="green")
        table.add_column("ID", style="dim")
        table.add_column("URL", style="blue")
        table.add_column("Default Branch", style="yellow")

        for repo in repos:
            table.add_row(
                repo.name,
                repo.id,
                repo.remote_url,
                repo.default_branch or "N/A"
            )

        console.print(table)

    except AdoClientError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)
```

**Repository Properties Used**:
- `name`: Repository name
- `id`: Repository GUID
- `remote_url`: Git clone URL (HTTPS)
- `default_branch`: Default branch reference (e.g., "refs/heads/main")

**Additional Properties Available** (for future enhancements):
- `ssh_url`: Git clone URL (SSH)
- `web_url`: Browser URL
- `project.name`: Project name
- `project.id`: Project GUID
- `size`: Repository size in bytes

**Pretty Printing with Rich**:

The command uses the `rich` library for formatted table output:
- **Table with borders**: Clean, professional table formatting
- **Colors**: Syntax highlighting for better readability
  - Name: Green
  - ID: Dim (gray)
  - URL: Blue
  - Default Branch: Yellow
- **Header styling**: Bold cyan headers
- **Responsive**: Adjusts to terminal width

**Rich Features Used**:
```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(show_header=True, header_style="bold cyan")
table.add_column("Name", style="green")
table.add_column("ID", style="dim")
table.add_column("URL", style="blue")
table.add_column("Default Branch", style="yellow")
console.print(table)
```

**Dependency**:
Add to `pyproject.toml`:
```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "rich (>=13.0.0,<14.0.0)"
]
```



The command constructs an Azure DevOps repository URL using:

1. **Server, Organization, Project, Repo Name**: Extracted from the git remote URL
2. **Branch**: Uses `--branch` option if provided, otherwise uses current git branch from `get_current_branch()`

### Git Remote URL Parsing

Azure DevOps remote URLs follow these formats:

**HTTPS Format:**
```
https://dev.azure.com/{org}/{project}/_git/{repo}
https://{org}@dev.azure.com/{org}/{project}/_git/{repo}
```

**SSH Format:**
```
git@ssh.dev.azure.com:v3/{org}/{project}/{repo}
```

**On-Premises Format:**
```
https://{server}/{org}/{project}/_git/{repo}
```

The parser should extract `server`, `org`, `project`, and `repo` from these formats. For cloud URLs (dev.azure.com), the server is normalized to `https://dev.azure.com`. For on-premises URLs, the actual server hostname is preserved.

### Azure DevOps URL Format

The browser will open:
```
{server}/{org}/{project}/_git/{repo}?version=GB{branch}
```

**Examples**:
```
https://dev.azure.com/myorg/myproject/_git/myrepo?version=GBmain
https://tfs.company.com/contoso/MyProject/_git/MyRepo?version=GBdevelop
```

If no branch is specified (neither via option nor current branch), omit the `?version=GB{branch}` parameter.

## Error Handling

### Not in a Git Repository
**Condition**: Current directory is not within a git repository
**Message**: `Error: Not in a git repository`
**Exit Code**: 1

### No Remote Found
**Condition**: Git repository has no remote named "origin"
**Message**: `Error: No remote 'origin' found`
**Exit Code**: 1

### Invalid Remote URL Format
**Condition**: Remote URL cannot be parsed as an Azure DevOps URL
**Message**: `Error: Remote URL is not a valid Azure DevOps repository URL`
**Exit Code**: 1

### Cannot Determine Branch
**Condition**: No `--branch` option provided and cannot get current branch
**Behavior**: Opens repository URL without branch parameter
**Note**: This is not an error - the URL will still open to the repository's default view

## Success Output

When successful, display:
```
Opening: {server}/{org}/{project}/_git/{repo}?version=GB{branch}
```

Then open the URL in the default browser.

**Example outputs**:
```
Opening: https://dev.azure.com/myorg/myproject/_git/myrepo?version=GBmain
Opening: https://tfs.company.com/contoso/MyProject/_git/MyRepo?version=GBdevelop
```

## Implementation Notes

### Dependencies
- `src.common.git_utils`: For `is_git_repository()`, `get_remote_url()`, `get_current_branch()`
- `src.common.ado_utils`: For `parse_ado_remote_url()`, `build_ado_repo_url()`
- `webbrowser` module: For opening URLs in default browser

### URL Parser Function

Implemented in `src.common.ado_utils.py`:
```python
def parse_ado_remote_url(remote_url: str) -> Optional[tuple[str, str, str, str]]:
    """
    Parse Azure DevOps remote URL to extract server, org, project, and repo.

    Args:
        remote_url: Git remote URL

    Returns:
        Tuple of (server, org, project, repo) if valid ADO URL, None otherwise.
        server will be "https://dev.azure.com" for cloud, or the actual server for on-premises.
    """
```

**Parsing Strategy**:
1. Try HTTPS pattern: `https://(?:[^@]+@)?([^/]+)/([^/]+)/([^/]+)/_git/([^/\s]+?)(?:\.git)?$`
2. Try SSH pattern: `git@ssh\.dev\.azure\.com:v3/([^/]+)/([^/]+)/([^/\s]+?)(?:\.git)?$`
3. Return None if no pattern matches

**Server Normalization**:
- Cloud URLs containing "dev.azure.com" → normalize to `https://dev.azure.com`
- On-premises URLs → preserve actual server URL as `https://{server}`

### URL Builder Function

Implemented in `src.common.ado_utils.py`:
```python
def build_ado_repo_url(server: str, org: str, project: str, repo: str, branch: Optional[str] = None) -> str:
    """
    Build Azure DevOps repository URL.

    Args:
        server: Server base URL (e.g., "https://dev.azure.com" or on-premises server)
        org: Organization name
        project: Project name
        repo: Repository name
        branch: Optional branch name

    Returns:
        Full Azure DevOps repository URL
    """
```

**URL Construction**:
1. Base URL: `{server}/{org}/{project}/_git/{repo}`
2. If branch provided: append `?version=GB{branch}`
3. Return complete URL

### Git Utilities

Implemented in `src.common.git_utils.py`:

```python
def is_git_repository(path: Path) -> bool:
    """Check if path is within a git repository."""

def get_remote_url(remote_name: str, path: Path) -> Optional[str]:
    """Get the URL of a git remote."""

def get_current_branch(path: Path) -> Optional[str]:
    """Get the current git branch name."""
```

## Technical Implementation

See [../cli_design.md](../cli_design.md) for common CLI implementation patterns.

**Repo-specific notes:**
- Parse remote URLs using regex patterns
- Handle both .git suffix and no suffix in remote URLs
- Preserve URL encoding in project names (e.g., `My%20Project`)
- Handle branch names with slashes (e.g., `feature/new-feature`)
- Repository names may contain dots (e.g., `my.repo.name`)
