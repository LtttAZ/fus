# CLI Design Guidelines

This document contains common design patterns and technical implementation notes that apply to all CLIs in this project.

## Common Technical Stack

All CLIs in this project use the following technologies:

- **CLI Framework**: Typer - Modern CLI framework with type hints and built-in testing support
- **Configuration Management**: pydantic-settings - Type-safe config management with validation
- **Config Directory**: platformdirs - Cross-platform config directory paths
- **Config Format**: PyYAML - YAML format for configuration files

## Configuration File Conventions

### Location
All CLI configuration files are stored in the user's config directory:
- Unix/Linux/macOS: `~/.fus/<cli_name>.yaml`
- Windows: `%LOCALAPPDATA%\fus\<cli_name>.yaml`

### Format
Configuration files use YAML format for readability and structure.

### Implementation Pattern
- Config models should use `BaseSettings` from pydantic-settings
- Use platformdirs to get the correct config directory path
- Configuration files should be readable and writable using PyYAML operations
- When updating config, preserve existing values and only modify specified fields

## Testing Approach

- Write integration tests using Typer's `CliRunner`
- Tests should verify end-to-end CLI behavior
- Test configuration isolation by using temporary directories
