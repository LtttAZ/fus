# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python CLI project named "fus" using Poetry for dependency management. The project requires Python 3.13.2 exactly.

**Multiple CLIs:** This repository contains multiple CLI tools. Each CLI is run directly using Python (not compiled to executables).

**Running CLIs:**
```bash
poetry run python <cli_script>.py [args]
```

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
- Config files stored in `~/.fus/<cli>.config` (Unix) or `AppData/Local/fus/<cli>.config` (Windows)
- Easy to override config directory in tests for isolation

Example config pattern:
```python
from pydantic_settings import BaseSettings
from platformdirs import user_config_dir

class CliConfig(BaseSettings):
    api_key: str
    timeout: int = 30

    class Config:
        # Override in tests by passing different path
        env_file = Path(user_config_dir("fus")) / "cli.config"
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
