# ADO Work Item Commands - Design Document

## Overview

The `ado workitem` (alias: `ado wi`) commands provide operations for Azure DevOps work items. These commands use configuration settings to construct work item URLs.

## Commands

### workitem browse

**Purpose**: Open a work item in the default web browser using configuration settings.

**Command**: `ado workitem browse --id=<id>` or `ado wi browse --id=<id>`

**Aliases**:
- `workitem` (full name)
- `wi` (short alias)

**Options**:
- `--id` (required): Work item ID number

**Behavior**:
1. Reads configuration from `~/.fus/ado.yaml`
2. Retrieves server (defaults to `https://dev.azure.com`), org, and project
3. Validates that org and project are configured
4. Constructs work item URL: `{server}/{org}/{project}/_workitems/edit/{id}`
5. Opens the URL in the default browser

**Exit Codes**:
- `0`: Success
- `1`: Error (missing config, invalid ID, etc.)
- `2`: Missing required option (Typer default)

**Example Usage**:
```bash
# Set up configuration first
ado config set --org myorg --project myproject

# Browse work item (full command)
ado workitem browse --id 12345

# Browse work item (short alias)
ado wi browse --id 67890

# With custom server (on-premises)
ado config set --server https://tfs.company.com
ado wi browse --id 12345
```

## Configuration Requirements

The command reads from `~/.fus/ado.yaml`:
- `server` (optional): Server URL, defaults to `https://dev.azure.com`
- `org` (required): Organization name
- `project` (required): Project name

**Example Configuration**:
```yaml
org: myorganization
project: myproject
server: https://dev.azure.com
```

## URL Construction

### Azure DevOps Work Item URL Format

The browser will open:
```
{server}/{org}/{project}/_workitems/edit/{id}
```

**Examples**:
```
https://dev.azure.com/myorg/myproject/_workitems/edit/12345
https://tfs.company.com/myorg/myproject/_workitems/edit/67890
```

### Server Default

If `server` is not set in configuration, defaults to `https://dev.azure.com` (Azure DevOps cloud).

## Error Handling

### Organization Not Configured
**Condition**: Config file doesn't contain `org` key
**Message**: `Error: Organization not configured. Use 'ado config set --org <org>' to set it.`
**Exit Code**: 1

### Project Not Configured
**Condition**: Config file doesn't contain `project` key
**Message**: `Error: Project not configured. Use 'ado config set --project <project>' to set it.`
**Exit Code**: 1

### Missing Work Item ID
**Condition**: `--id` option not provided
**Message**: Typer will display usage help showing `--id` is required
**Exit Code**: 2 (Typer default for missing required options)

## Success Output

When successful, display:
```
Opening: {server}/{org}/{project}/_workitems/edit/{id}
```

Then open the URL in the default browser.

**Example outputs**:
```
Opening: https://dev.azure.com/myorg/myproject/_workitems/edit/12345
Opening: https://tfs.company.com/contoso/MyProject/_workitems/edit/67890
```

## Implementation Notes

### Dependencies
- `src.common.ado_config`: For `AdoConfig` class
- `src.common.ado_utils`: For `build_ado_workitem_url()`
- `webbrowser` module: For opening URLs in default browser

### URL Builder Function

Implemented in `src.common.ado_utils.py`:
```python
def build_ado_workitem_url(server: str, org: str, project: str, workitem_id: int) -> str:
    """
    Build Azure DevOps work item URL.

    Args:
        server: Server base URL (e.g., "https://dev.azure.com" or on-premises server)
        org: Organization name
        project: Project name
        workitem_id: Work item ID

    Returns:
        Full Azure DevOps work item URL
    """
    return f"{server}/{org}/{project}/_workitems/edit/{workitem_id}"
```

### Command Aliases

The command is accessible via two aliases:
- `ado workitem browse` (full name)
- `ado wi browse` (short alias)

**Implementation**:
```python
workitem_app = typer.Typer(help="Work item commands")
app.add_typer(workitem_app, name="workitem")
app.add_typer(workitem_app, name="wi")
```

Both aliases use the same Typer app instance, registered twice with different names.

### Configuration Validation

The command uses the `AdoConfig` class for simplified configuration access with automatic validation:

```python
@workitem_app.command("browse")
def workitem_browse(id: int = typer.Option(..., "--id", help="Work item ID")):
    """Open a work item in the default web browser."""
    config = AdoConfig()
    url = build_ado_workitem_url(config.server, config.org, config.project, id)
    typer.echo(f"Opening: {url}")
    webbrowser.open(url)
```

**How AdoConfig works:**
1. Loads configuration from `~/.fus/ado.yaml` automatically
2. `config.server` - Returns configured server or defaults to `https://dev.azure.com`
3. `config.org` - Returns org if configured, otherwise exits with helpful error message
4. `config.project` - Returns project if configured, otherwise exits with helpful error message

**Benefits:**
- Configuration validation is centralized in the `AdoConfig` class
- Error handling happens automatically when accessing properties
- CLI code is concise and readable (4 lines instead of ~25)
- See [config_design.md](config_design.md) for AdoConfig class details

## Technical Implementation

See [../cli_design.md](../cli_design.md) for common CLI implementation patterns.

**Workitem-specific notes:**
- Configuration is required (unlike repo commands which can extract info from git remote)
- Server defaults to Azure DevOps cloud if not configured
- Work item IDs are integers
- Error messages should guide users to set missing config values using `ado config set`
- The `--id` option is required (not optional like other command options)
