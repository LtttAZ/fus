# ADO Config Commands - Design Document

## Overview

The `ado config` commands manage configuration settings for the ADO CLI tool. Configuration is stored in a YAML file and used by other commands.

## Commands

### config set

**Purpose**: Store Azure DevOps configuration values for the CLI.

**Command**: `ado config set`

**Options**:
- `--project` (optional): The Azure DevOps project name
- `--org` (optional): The Azure DevOps organization name
- `--server` (optional): The Azure DevOps server URL (defaults to `https://dev.azure.com` if not set)

**Behavior**:
1. Accepts one or more configuration options
2. At least one option must be provided
3. Stores the provided values in a configuration file at `~/.fus/ado.yaml`
4. Creates the `~/.fus/` directory if it doesn't exist
5. If `ado.yaml` exists, updates only the specified values (preserves other existing values)
6. If `ado.yaml` doesn't exist, creates it with the provided values
7. Displays success message listing the saved values, e.g., "Configuration saved: project=MyProject, org=MyOrg"

**Exit Codes**:
- `0`: Success
- `1`: Error (no options provided, filesystem error, etc.)

**Error Handling**:
- If no options are provided, display error message "At least one configuration option must be provided" and exit with code 1
- If filesystem errors occur (permissions, disk full, etc.), display error message and exit with code 1

**Example Usage**:
```bash
ado config set --project MyProject --org MyOrg
ado config set --server https://dev.azure.com
ado config set --project NewProject  # Updates only project, preserves org
ado config set --server https://tfs.company.com  # On-premises server
```

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
- `project`: Azure DevOps project name (used by workitem commands)
- `org`: Azure DevOps organization name (used by workitem commands)
- `server`: Azure DevOps server URL (defaults to `https://dev.azure.com` if not set, used by workitem commands)

## Implementation Notes

### Dependencies
- `src.common.ado_config`: For `get_config_path()`, `read_config()`, `write_config()`
- `platformdirs`: For cross-platform config directory paths
- `PyYAML`: For YAML file operations

### Config Functions

Implemented in `src.common.ado_config.py`:

```python
def get_config_path() -> Path:
    """Get the path to the ado.yaml config file."""
    config_dir = Path(user_config_dir("fus"))
    return config_dir / "ado.yaml"

def read_config(config_path: Path) -> dict:
    """Read and parse the YAML config file."""
    # Returns empty dict if file doesn't exist
    # Returns parsed YAML content as dict

def write_config(config_path: Path, config: dict) -> None:
    """Write config dictionary to YAML file."""
    # Creates parent directory if it doesn't exist
    # Writes config as YAML
```

### Update Behavior

When updating configuration:
1. Read existing config (if file exists)
2. Merge new values into existing config
3. Write merged config back to file
4. Preserve any keys not being updated

This allows users to set values incrementally without losing previous settings.

## Technical Implementation

See [../cli_design.md](../cli_design.md) for common CLI implementation patterns.

**Config-specific notes:**
- Use `platformdirs.user_config_dir("fus")` to get the config directory path
- Config file should be readable and writable using `yaml.safe_load()` and `yaml.dump()`
- When updating config, merge with existing values (don't overwrite entire file)
- Create parent directories with `mkdir(parents=True, exist_ok=True)` before writing
