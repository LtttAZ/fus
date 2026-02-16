# ADO CLI Design Document

## Overview

**Cross-Platform CLI**: Runs on Windows (Command Prompt, PowerShell, Git Bash), Linux, and macOS.

The `ado` CLI provides commands for interacting with Azure DevOps. Supports configuration management, repository browsing, and work item operations.

## Command Structure

```bash
# Configuration commands
ado config set [--project=<project>] [--org=<organization>] [--server=<server>]
ado config list

# Repository commands
ado repo browse [--branch=<branch>]
ado repo list [--pattern=<pattern>]

# Work item commands
ado workitem browse --id=<id>
ado wi browse --id=<id>          # Alias for workitem
```

## Command Groups

### Configuration Commands
Manage ADO CLI configuration settings.

**Detailed design**: [config_design.md](config_design.md)

**Commands**:
- `ado config set` - Set configuration values (project, org, server)
- `ado config list` - List all current configuration values

### Repository Commands
Operations for Azure DevOps repositories.

**Detailed design**: [repo_design.md](repo_design.md)

**Commands**:
- `ado repo browse` - Open repository in browser (uses git remote URL)
- `ado repo list` - List all repositories in project with optional pattern filtering (uses API, requires ADO_PAT)

### Work Item Commands
Operations for Azure DevOps work items using configuration settings.

**Detailed design**: [workitem_design.md](workitem_design.md)

**Commands**:
- `ado workitem browse` (alias: `ado wi browse`) - Open work item in browser

## API Client

For programmatic interaction with Azure DevOps REST API.

**Detailed design**: [client_design.md](client_design.md)

**Purpose:**
- Provide Python API for Azure DevOps operations
- Enable CLI commands to retrieve data from Azure DevOps (beyond URL generation)
- Support authentication with Personal Access Tokens (PAT)

**Initial scope:**
- Repository operations: list repositories, get repository details

**Future features:**
- Work item CRUD operations
- Pull request management
- Pipeline operations

## Configuration File

**Location** (via `platformdirs.user_config_dir("fus")`):
- **Windows**: `%LOCALAPPDATA%\fus\ado.yaml`
- **Linux**: `~/.config/fus/ado.yaml`
- **macOS**: `~/Library/Application Support/fus/ado.yaml`

**Format**: YAML

**Example**:
```yaml
project: MyProject
org: MyOrganization
server: https://dev.azure.com
```

**Configuration Keys**:
- `project`: Azure DevOps project name (required for work item commands and repo list)
- `org`: Azure DevOps organization name (required for work item commands and repo list)
- `server`: Azure DevOps server URL (defaults to `https://dev.azure.com` if not set)

**Note:** Personal Access Token (PAT) for API operations is configured via the `ADO_PAT` environment variable, not in the config file. Required for: `ado repo list`. See [client_design.md](client_design.md) for details.

## Quick Examples

```bash
# Set up configuration
ado config set --project MyProject --org MyOrg
ado config set --server https://dev.azure.com

# List current configuration
ado config list

# Set up PAT for API operations (required for repo list)
export ADO_PAT="your-personal-access-token"  # Linux/macOS/Git Bash
set ADO_PAT=your-personal-access-token       # Windows Command Prompt
$env:ADO_PAT="your-personal-access-token"    # Windows PowerShell

# Browse repository (current directory must be a git repo)
ado repo browse
ado repo browse --branch develop

# List repositories in project (requires ADO_PAT)
ado repo list
ado repo list --pattern "my-*"         # Filter by pattern
ado repo list --patt "*-service"       # Using alias

# Browse work item
ado wi browse --id 12345
```

## Technical Implementation

See [../cli_design.md](../cli_design.md) for common CLI implementation patterns.

**ADO CLI Implementation**:
- CLI entry point: `src/cli/ado.py`
- Configuration utilities: `src/common/ado_config.py`
- ADO URL utilities: `src/common/ado_utils.py`
- ADO REST API client: `src/common/ado_client.py` (see [client_design.md](client_design.md))
- Git utilities: `src/common/git_utils.py`
- Integration tests: `tests/ado/`

**Module Structure**:
```python
# src/cli/ado.py
app = typer.Typer(help="Azure DevOps CLI tool")
config_app = typer.Typer(help="Manage configuration")
repo_app = typer.Typer(help="Repository commands")
workitem_app = typer.Typer(help="Work item commands")

app.add_typer(config_app, name="config")
app.add_typer(repo_app, name="repo")
app.add_typer(workitem_app, name="workitem")
app.add_typer(workitem_app, name="wi")  # Alias
```

## Supported Azure DevOps Environments

The ADO CLI supports both:
- **Azure DevOps Services** (cloud): `https://dev.azure.com`
- **Azure DevOps Server** (on-premises): Custom server URLs (e.g., `https://tfs.company.com`)

The `--server` configuration option allows users to specify on-premises installations.
