# fus

A collection of Python CLI tools.

## Requirements

- Python 3.13.2 (exact version)
- Poetry for dependency management

## Technology Stack

- **CLI Framework**: Typer - Modern CLI framework with type hints and built-in testing support
- **Configuration Management**:
  - pydantic-settings - Type-safe config management with validation
  - platformdirs - Cross-platform config directory paths (~/.fus on Unix, AppData on Windows)

## Setup

```bash
# Activate virtual environment (Windows Git Bash)
source .venv/Scripts/activate

# Install dependencies
poetry install
```

## Running CLIs

Each CLI is run directly using Python:

```bash
poetry run python src/<cli_name>/<cli_name>.py [args]
```

## Project Structure

```
fus/
├── docs/                    # Design documents
│   └── <cli_name>/         # Design docs for specific CLI
│       └── design.md       # Feature design document
├── src/                     # Source code
│   ├── common/             # Shared modules used by multiple CLIs
│   │   ├── __init__.py
│   │   └── ...             # Common utilities, helpers, etc.
│   └── <cli_name>/         # Each CLI in its own directory
│       ├── __init__.py
│       ├── <cli_name>.py   # Main CLI entry point
│       └── ...             # Supporting modules
├── tests/                   # Integration tests
│   ├── common/             # Tests for common modules
│   │   └── test_*.py
│   └── <cli_name>/         # Tests for specific CLI
│       └── test_*.py       # Test files
├── pyproject.toml          # Poetry configuration
├── CLAUDE.md               # Development guidelines for Claude Code
└── README.md               # This file
```

## Development Workflow

This project follows a **document-first, test-driven development** approach:

1. **Design Document Phase**: Co-author design documents in `docs/<cli_name>/`
2. **Test-Driven Development**: Create integration tests in `tests/<cli_name>/` based on the design
3. **Implementation**: Implement the CLI in `src/<cli_name>/` to make tests pass

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

## Adding a New CLI

1. Create design document: `docs/<cli_name>/design.md`
2. Create CLI directory: `src/<cli_name>/`
3. Create test directory: `tests/<cli_name>/`
4. Follow the TDD workflow
