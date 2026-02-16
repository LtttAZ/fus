# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python CLI project named "fus" using Poetry for dependency management. The project requires Python 3.13.2 exactly.

**Multiple CLIs:** This repository contains multiple CLI tools. Each CLI is run directly using Python (not compiled to executables).

**Running CLIs:**

From anywhere (if `scripts/` directory is in system PATH):
```bash
<cli_name> [args]
```

From project directory:
```bash
poetry run python src/cli/<cli_name>.py [args]
```

**Wrapper Scripts:** The `scripts/` directory contains batch files (`.bat`) for each CLI. These scripts activate the venv and call the CLI while preserving the caller's current directory for relative paths.

## Development Setup

The project uses Poetry with a virtual environment located in `.venv/`.

### Environment Setup
```bash
# Activate virtual environment (Windows Git Bash)
source .venv/Scripts/activate

# Install dependencies
poetry install
```

### Common Commands

```bash
# Add a new dependency
poetry add <package>

# Add a development dependency
poetry add --group dev <package>

# Update dependencies
poetry update

# Run a command in the Poetry environment
poetry run python <script>

# Install the project in editable mode
poetry install
```

## Python Version

The project strictly requires Python 3.13.2 (not >=3.13, but ==3.13.2). This is specified in `pyproject.toml`.

## Technology Stack

**CLI Framework:** Typer
- Modern CLI framework built on Click
- Uses type hints for parameter validation
- Built-in `CliRunner` for easy integration testing
- Rich terminal output support

**Configuration Management:**
- **pydantic-settings**: Type-safe config management using Pydantic models
- **platformdirs**: Cross-platform config directory paths
- **PyYAML**: YAML format for configuration files
- Config files stored in `~/.fus/<cli>.yaml` (Unix) or `AppData/Local/fus/<cli>.yaml` (Windows) in YAML format
- Easy to override config directory in tests for isolation

**Code Organization:**
- **Segregation of Duties**: CLI entry points (`src/cli/`) define only the CLI structure (commands, options). Business logic and CRUD operations are implemented in common modules (`src/common/`).
- CLI files should be minimal and focused on Typer definitions
- Common modules provide reusable functions for config management, data operations, etc.
- See [docs/cli_design.md](docs/cli_design.md) for detailed patterns

Example config pattern:
```python
# src/common/<cli>_config.py - Business logic
from pathlib import Path
from platformdirs import user_config_dir
import yaml

def get_config_path() -> Path:
    return Path(user_config_dir("fus")) / "cli.yaml"

def read_config(config_path: Path) -> dict:
    if not config_path.exists():
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}

def write_config(config_path: Path, config: dict) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
```

## Development Workflow

This project follows a **document-first, test-driven development** approach:

### 1. Design Document Phase
- Co-author design documents for new features/CLIs
- Document should clearly define requirements, behavior, and interfaces
- Get approval before proceeding to tests

### 2. Test-Driven Development (TDD)
- Create integration tests based on the approved design document
- Tests should cover the behavior specified in the design
- User reviews and approves tests before implementation

### 3. Implementation
- Implement features only after tests are approved
- Code should make the tests pass

### Testing Guidelines
- Write integration tests that verify end-to-end CLI behavior
- Use Typer's `CliRunner` to invoke commands programmatically in tests
- Tests must be approved before starting implementation

Example test pattern:
```python
from typer.testing import CliRunner
runner = CliRunner()
result = runner.invoke(app, ["arg1", "arg2"])
assert result.exit_code == 0
assert "expected output" in result.stdout
```
