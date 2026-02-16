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

**Configuration**:
- `repo.columns`: Comma-separated list of field paths to display (configurable via `ado config set`)
  - Default: `name,id,remote_url,default_branch`
  - Supports dot notation for nested fields: `project.name`, `project.id`
  - Automatically parses JSON strings in nested field access

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

Display repositories in a formatted table using `rich`. Columns are configurable via `repo.columns` config.

**Default fields** (`name,id,remote_url,default_branch`):

```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ name         ┃ id                                   ┃ remote_url                                                    ┃ default_branch   ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ my-repo      │ 2f3d611a-f012-4b39-b157-8db63f380226 │ https://dev.azure.com/myorg/myproject/_git/my-repo            │ refs/heads/main  │
│ another-repo │ 8a4b722c-e023-5c40-c268-9fc74e7f6e3e │ https://dev.azure.com/myorg/myproject/_git/another-repo       │ refs/heads/master│
└──────────────┴──────────────────────────────────────┴───────────────────────────────────────────────────────────────┴──────────────────┘
```

**Custom fields** (e.g., `name,web_url,project.name`):

```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ name         ┃ web_url                                                                   ┃ project.name┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ my-repo      │ https://dev.azure.com/myorg/myproject/_git/my-repo                        │ MyProject   │
│ another-repo │ https://dev.azure.com/myorg/myproject/_git/another-repo                   │ MyProject   │
└──────────────┴───────────────────────────────────────────────────────────────────────────┴─────────────┘
```

**Configuring fields**:
```bash
# Set custom fields
ado config set repo.columns=name,web_url,project.name

# Reset to default
ado config set repo.columns=name,id,remote_url,default_branch

# Minimal view
ado config set repo.columns=name,remote_url

# Access nested fields
ado config set repo.columns=name,project.id,project.name
```

**Field Access**:

Fields support dot notation for nested access:
- `name` - Repository name
- `id` - Repository GUID
- `remote_url` - Git clone URL (HTTPS)
- `ssh_url` - Git clone URL (SSH)
- `web_url` - Browser URL
- `default_branch` - Default branch reference
- `size` - Repository size in bytes
- `project.name` - Project name (nested field)
- `project.id` - Project GUID (nested field)

Any field from the GitRepository object can be accessed. If a nested value is a JSON string instead of an object, it will be automatically parsed before continuing field access.

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

**Field Access Error**:
- Message:
  ```
  Error: Unable to access field 'invalid.field.path' on repository object
  ```
- Exit Code: 1

**Implementation Notes**:

**Dependencies**:
- `src.common.ado_client`: For `AdoClient`
- `src.common.ado_exceptions`: For `AdoClientError`, `AdoAuthError`, `AdoNotFoundError`
- `src.common.ado_config`: For `AdoConfig`
- `rich`: For table formatting and pretty output

**Implementation Pattern**:
```python
import json
from rich.console import Console
from rich.table import Table

DEFAULT_FIELDS = ["name", "id", "remote_url", "default_branch"]

def get_nested_value(obj, field_path: str):
    """
    Get nested value from object using dot notation.

    If a nested value is a JSON string, parse it before continuing.

    Args:
        obj: Object to access
        field_path: Dot-separated path (e.g., "project.name")

    Returns:
        The value at the field path

    Raises:
        AttributeError: If field path is invalid
    """
    parts = field_path.split(".")
    current = obj

    for part in parts:
        # Get the attribute
        current = getattr(current, part)

        # If it's a string and we have more parts to traverse, try parsing as JSON
        if isinstance(current, str) and parts.index(part) < len(parts) - 1:
            try:
                current = json.loads(current)
            except (json.JSONDecodeError, TypeError):
                # Not valid JSON or not a string, continue with the object as-is
                pass

    return current

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

        # Get fields configuration
        fields_config = client.config._data.get("repo", {}).get("columns")
        if fields_config:
            fields = [f.strip() for f in fields_config.split(",")]
        else:
            fields = DEFAULT_FIELDS

        # Create rich table
        console = Console()
        table = Table(show_header=True, header_style="bold cyan")

        # Add columns with field names as headers
        for field in fields:
            table.add_column(field)

        # Add rows
        for repo in repos:
            row = []
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
```

**Repository Properties Used**:
- `name`: Repository name
- `id`: Repository GUID
- `remote_url`: Git clone URL (HTTPS)
- `default_branch`: Default branch reference (e.g., "refs/heads/main")

**Additional Properties Available**:
- `ssh_url`: Git clone URL (SSH)
- `web_url`: Browser URL
- `project.name`: Project name (nested field)
- `project.id`: Project GUID (nested field)
- `size`: Repository size in bytes
- Any other field from the GitRepository object

**Nested Field Access**:

The `get_nested_value()` helper function supports:
1. Dot notation for nested fields: `project.name`, `project.id`
2. Automatic JSON parsing: If a nested value is a JSON string, it's parsed before continuing
3. Safe error handling: Returns error if field path is invalid

**Example nested access**:
```python
# Direct attribute
value = get_nested_value(repo, "name")  # returns repo.name

# Nested attribute
value = get_nested_value(repo, "project.name")  # returns repo.project.name

# With JSON parsing (if project is a JSON string)
# 1. Gets repo.project (a string)
# 2. Parses it as JSON
# 3. Accesses .name on the parsed object
value = get_nested_value(repo, "project.name")
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
