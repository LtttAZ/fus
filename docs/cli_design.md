# CLI Design Guidelines

This document contains common design patterns and technical implementation notes that apply to all CLIs in this project.

## Code Organization Pattern

### Segregation of Duties

The project follows a clear separation of concerns:

**CLI Entry Points (`src/cli/<cli_name>.py`)**:
- Define CLI structure using Typer (commands, subcommands, options)
- Handle user input validation and command routing
- Display output and error messages
- Keep business logic minimal - delegate to common modules

**Common Modules (`src/common/`)**:
- Implement business logic, data operations, and CRUD functions
- Handle configuration file reading/writing
- Provide reusable utilities and helpers
- Can be tested independently of CLI interface

**Example**:
```python
# src/cli/ado.py - CLI definition only
import typer
from src.common.ado_config import get_config_path, read_config, write_config

@config_app.command("set")
def config_set(project: Optional[str] = typer.Option(None, "--project")):
    config_path = get_config_path()
    config = read_config(config_path)
    if project:
        config["project"] = project
    write_config(config_path, config)
    typer.echo(f"Configuration saved: project={project}")

# src/common/ado_config.py - Business logic
def get_config_path() -> Path:
    """Get the path to the ado.yaml config file."""
    return Path(user_config_dir("fus")) / "ado.yaml"

def read_config(config_path: Path) -> dict:
    """Read and parse the YAML config file."""
    # ... implementation ...

def write_config(config_path: Path, config: dict) -> None:
    """Write config dictionary to YAML file."""
    # ... implementation ...
```

This separation provides:
- **Reusability**: Common modules can be shared across CLIs
- **Testability**: Business logic can be tested independently
- **Maintainability**: Clear boundaries between interface and implementation
- **Clarity**: CLI files show structure at a glance

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
