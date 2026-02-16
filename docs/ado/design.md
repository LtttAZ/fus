# ADO CLI Design Document

## Overview

The `ado` CLI provides commands for interacting with Azure DevOps. It supports configuration management, repository browsing, and work item operations.

## Command Structure

```bash
# Configuration commands
ado config set [--project=<project>] [--org=<organization>] [--server=<server>]
ado config list

# Repository commands
ado repo browse [--branch=<branch>]

# Work item commands
ado workitem browse --id=<id>
ado wi browse --id=<id>          # Alias for workitem
```

## Command Groups

### Configuration Commands
Manage ADO CLI configuration settings stored in `~/.fus/ado.yaml`.

**Detailed design**: [config_design.md](config_design.md)

**Commands**:
- `ado config set` - Set configuration values (project, org, server)
- `ado config list` - List all current configuration values

### Repository Commands
Operations for Azure DevOps repositories using git remote information.

**Detailed design**: [repo_design.md](repo_design.md)

**Commands**:
- `ado repo browse` - Open repository in browser

### Work Item Commands
Operations for Azure DevOps work items using configuration settings.

**Detailed design**: [workitem_design.md](workitem_design.md)

**Commands**:
- `ado workitem browse` (alias: `ado wi browse`) - Open work item in browser

## Configuration File

**Location**: `~/.fus/ado.yaml` (Unix/Linux/macOS) or `%LOCALAPPDATA%\fus\ado.yaml` (Windows)

**Format**: YAML

**Example**:
```yaml
project: MyProject
org: MyOrganization
server: https://dev.azure.com
```

**Configuration Keys**:
- `project`: Azure DevOps project name (required for work item commands)
- `org`: Azure DevOps organization name (required for work item commands)
- `server`: Azure DevOps server URL (defaults to `https://dev.azure.com` if not set)

## Quick Examples

```bash
# Set up configuration
ado config set --project MyProject --org MyOrg
ado config set --server https://dev.azure.com

# List current configuration
ado config list

# Browse repository (current directory must be a git repo)
ado repo browse
ado repo browse --branch develop

# Browse work item
ado wi browse --id 12345
```

## Technical Implementation

See [../cli_design.md](../cli_design.md) for common CLI implementation patterns.

**ADO CLI Implementation**:
- CLI entry point: `src/cli/ado.py`
- Configuration utilities: `src/common/ado_config.py`
- ADO URL utilities: `src/common/ado_utils.py`
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
