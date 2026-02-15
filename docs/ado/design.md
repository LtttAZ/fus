# ADO CLI Design Document

## Overview

The `ado` CLI provides commands for interacting with Azure DevOps. This document defines the initial `config set` command for managing CLI configuration.

## Command Structure

```bash
ado config set --project=<project>
```

## Features

### Config Set Command

**Purpose**: Store Azure DevOps project configuration for the CLI.

**Command**: `ado config set`

**Options**:
- `--project` (required): The Azure DevOps project name to store in configuration

**Behavior**:
1. Accepts a project name via the `--project` option
2. Stores the project value in a configuration file at `~/.fus/ado.config`
3. Creates the `~/.fus/` directory if it doesn't exist
4. Creates or overwrites the `ado.config` file with the new project value
5. Displays success message: "Configuration saved: project=<project>"

**Exit Codes**:
- `0`: Success
- `1`: Error (missing required option, filesystem error, etc.)

**Error Handling**:
- If `--project` option is not provided, display error and exit with code 1
- If filesystem errors occur (permissions, disk full, etc.), display error message and exit with code 1

## Configuration File Format

**Location**: `~/.fus/ado.config` (Unix/Linux/macOS) or `%LOCALAPPDATA%\fus\ado.config` (Windows)

**Format**: YAML

Example `ado.config`:
```yaml
project: MyProject
```

## Technical Implementation Notes

- Use Typer for CLI framework
- Use pydantic-settings for configuration management
- Use platformdirs to get the correct config directory path
- Use PyYAML for reading/writing YAML configuration files
- Config model should use `BaseSettings` from pydantic-settings
- The config file should be readable and writable using YAML operations

## Future Considerations

- Additional config options (organization, PAT token, default work item type, etc.)
- `ado config get` command to retrieve config values
- `ado config list` command to show all configuration
- `ado config unset` command to remove config values
- Validation of project name format (if Azure DevOps has requirements)
