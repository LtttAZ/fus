# ADO CLI Design Document

## Overview

The `ado` CLI provides commands for interacting with Azure DevOps. This document defines the initial `config set` command for managing CLI configuration.

## Command Structure

```bash
ado config set [--project=<project>] [--org=<organization>]
```

## Features

### Config Set Command

**Purpose**: Store Azure DevOps configuration values for the CLI.

**Command**: `ado config set`

**Options**:
- `--project` (optional): The Azure DevOps project name to store in configuration
- `--org` (optional): The Azure DevOps organization name to store in configuration

**Behavior**:
1. Accepts one or more configuration options (--project, --org, etc.)
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

## Configuration File Format

**Location**: `~/.fus/ado.yaml` (Unix/Linux/macOS) or `%LOCALAPPDATA%\fus\ado.yaml` (Windows)

**Format**: YAML

Example `ado.yaml`:
```yaml
project: MyProject
org: MyOrganization
```

## Technical Implementation Notes

See [../cli_design.md](../cli_design.md) for common CLI implementation patterns.

**ADO-specific notes:**
- The config file should be readable and writable using YAML operations
- When updating config, merge with existing values (don't overwrite entire file)

## Future Considerations

- Additional config options (organization, PAT token, default work item type, etc.)
- `ado config get` command to retrieve config values
- `ado config list` command to show all configuration
- `ado config unset` command to remove config values
- Validation of project name format (if Azure DevOps has requirements)
