# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python CLI project named "fus" using Poetry for dependency management. The project requires Python 3.13.2 exactly.

**Cross-Platform Support:** All CLI tools are designed to run on:
- Windows (Command Prompt, PowerShell, Git Bash)
- Linux (Bash)
- macOS (Bash/Zsh)

**Multiple CLIs:** This repository contains multiple CLI tools. Each CLI is run directly using Python (not compiled to executables).

**Running CLIs:**

From project directory (cross-platform):
```bash
poetry run python src/cli/<cli_name>.py [args]
```

From anywhere (if `scripts/` directory is in system PATH):
- **Windows**: `<cli_name>.bat [args]` (batch file wrapper)
- **Linux/macOS**: Add `scripts/` to PATH and use `poetry run python` wrapper scripts

**Note:** The `scripts/` directory contains `.bat` files for Windows. These activate the venv and call the CLI while preserving the caller's current directory for relative paths. For Linux/macOS, use `poetry run` directly or create shell script wrappers as needed.

## Development Setup

The project uses Poetry with a virtual environment located in `.venv/`.

### Environment Setup

**Activate virtual environment:**

```bash
# Windows Command Prompt
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows Git Bash / Linux / macOS
source .venv/bin/activate
```

**Install dependencies:**
```bash
poetry install
```

### Common Commands

**IMPORTANT: Always use Poetry for dependency management, never use pip directly.**

```bash
# Add a new dependency
poetry add <package>

# Add a development dependency
poetry add --group dev <package>

# Update dependencies
poetry update

# CRITICAL: Always run poetry lock after adding/updating dependencies
poetry lock

# Run a command in the Poetry environment (cross-platform)
poetry run python <script>

# Install the project in editable mode
poetry install

# Run tests (cross-platform)
poetry run pytest              # All tests
poetry run pytest -v           # Verbose output
poetry run pytest tests/ado/   # ADO tests only
```

**Platform-specific test commands** (if needed):
```bash
# Windows
.venv\Scripts\python -m pytest

# Linux/macOS
.venv/bin/python -m pytest
```

**Dependency Management Rules:**
- ✅ **DO**: Use `poetry add` to add dependencies
- ✅ **DO**: Run `poetry lock` after any dependency changes to update lock file
- ✅ **DO**: Commit both `pyproject.toml` and `poetry.lock` together
- ❌ **DON'T**: Use `pip install` - it bypasses Poetry's dependency resolution
- ❌ **DON'T**: Edit `pyproject.toml` manually without running `poetry lock`

## Python Version

The project strictly requires Python 3.13.2 (not >=3.13, but ==3.13.2). This is specified in `pyproject.toml`.

## Current CLIs

### ADO (Azure DevOps) CLI

The `ado` CLI provides commands for interacting with Azure DevOps. Supports both Azure DevOps Services (cloud) and Azure DevOps Server (on-premises).

**Commands:**
- `ado config set` - Set configuration (project, org, server)
- `ado repo browse` - Open repository in browser (from git remote)
- `ado workitem browse` (alias: `ado wi browse`) - Open work item in browser (requires config)

**Configuration:**
- **Windows**: `%LOCALAPPDATA%\fus\ado.yaml` (typically `C:\Users\<username>\AppData\Local\fus\ado.yaml`)
- **Linux/macOS**: `~/.local/share/fus/ado.yaml` or `~/.config/fus/ado.yaml` (depends on platformdirs)
- Uses `AdoConfig` class for validated access
- See [docs/ado/design.md](docs/ado/design.md) for details

**Implementation highlights:**
- Configuration class pattern with property-based validation
- Git remote URL parsing for repo commands
- Support for both cloud and on-premises Azure DevOps
- Comprehensive test coverage (36 tests)

## Technology Stack

**CLI Framework:** Typer
- Modern CLI framework built on Click
- Uses type hints for parameter validation
- Built-in `CliRunner` for easy integration testing
- Rich terminal output support

**Configuration Management:**
- **pydantic-settings**: Type-safe config management using Pydantic models
- **platformdirs**: Cross-platform config directory paths (automatically selects correct location per OS)
- **PyYAML**: YAML format for configuration files
- Config file locations (via `platformdirs.user_config_dir("fus")`):
  - **Windows**: `%LOCALAPPDATA%\fus\<cli>.yaml`
  - **Linux**: `~/.config/fus/<cli>.yaml` or `~/.local/share/fus/<cli>.yaml`
  - **macOS**: `~/Library/Application Support/fus/<cli>.yaml`
- Easy to override config directory in tests for isolation

**Code Organization:**
- **Segregation of Duties**: CLI entry points (`src/cli/`) define only the CLI structure (commands, options). Business logic and CRUD operations are implemented in common modules (`src/common/`).
- CLI files should be minimal and focused on Typer definitions
- Common modules provide reusable functions for config management, data operations, etc.
- See [docs/cli_design.md](docs/cli_design.md) for detailed patterns

**Configuration Pattern - Validation Classes:**

For CLIs that need validated configuration values, use a configuration class to centralize validation and error handling:

```python
# src/common/<cli>_config.py - Configuration class with validation
class AdoConfig:
    """ADO configuration with validation and error handling."""

    def __init__(self):
        """Load configuration from file."""
        self.config_path = get_config_path()
        self._data = read_config(self.config_path)

    @property
    def server(self) -> str:
        """Get server URL with default."""
        return self._data.get("server", "https://dev.azure.com")

    @property
    def org(self) -> str:
        """Get organization name, exits with error if not configured."""
        value = self._data.get("org")
        if not value:
            typer.echo("Error: Organization not configured. Use 'ado config set --org <org>' to set it.")
            raise typer.Exit(code=1)
        return value
```

**Benefits:**
- Centralizes all validation logic and error messages in one place
- Makes CLI code concise (reduced from ~25 lines to 4 lines)
- Automatic validation when properties are accessed
- Consistent error handling across all commands

**Basic Config Pattern (for simple configs):**

```python
# src/common/<cli>_config.py - Basic functions for simple config management
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
- Co-author design documents for new features/CLIs in `docs/<cli_name>/`
- Documents should clearly define requirements, behavior, and interfaces
- **Organize design docs by first-level commands** (e.g., `config_design.md`, `repo_design.md`, `workitem_design.md`)
- Main `design.md` provides overview and links to command-specific docs
- Get approval before proceeding to tests

### 2. Test-Driven Development (TDD)
- Create integration tests based on the approved design document
- Organize tests by command groups in `tests/<cli_name>/test_<command>_<subcommand>.py`
- Tests should cover the behavior specified in the design
- User reviews and approves tests before implementation

### 3. Implementation
- Implement features only after tests are approved
- Code should make the tests pass
- Keep CLI code concise by delegating to common modules
- Use configuration classes for validated config access
- **Run `poetry lock` after any dependency changes**

### 4. Documentation Update **[CRITICAL - DO NOT SKIP]**
- **ALWAYS check and update design documents after implementation**
- This is a required step, not optional - treat it with the same importance as writing tests
- Review all affected design docs for outdated information:
  - Command syntax changes
  - New options or flags
  - Implementation details (class names, function locations, patterns)
  - Configuration keys and defaults
  - Code examples that reference implementation
- Update docs to reflect actual implementation (not just planned design)
- Remove outdated information that contradicts current code
- Cross-reference related documents

### 5. Dependency Management
- **If dependencies were added/updated, run `poetry lock` before committing**
- Commit `pyproject.toml` and `poetry.lock` together

**Complete workflow checklist:**
1. ✅ Write feature design document
2. ✅ Write integration tests
3. ✅ Implement feature
4. ✅ **Check if docs need updates** (compare design vs implementation)
5. ✅ **Update design docs** to match actual implementation
6. ✅ **Run `poetry lock`** if dependencies changed
7. ✅ Commit all changes together (code + tests + docs + lock file)

### Testing Guidelines
- Write integration tests that verify end-to-end CLI behavior
- Use Typer's `CliRunner` to invoke commands programmatically in tests
- Tests must be approved before starting implementation
- Mock external dependencies (file system, network, etc.)

Example test pattern:
```python
from typer.testing import CliRunner
runner = CliRunner()
result = runner.invoke(app, ["arg1", "arg2"])
assert result.exit_code == 0
assert "expected output" in result.stdout
```

## Documentation Structure

### Design Document Organization

Design documents are organized by **first-level commands** to make it easy to find all related information:

```
docs/
├── README.md                    # Documentation index
├── cli_design.md                # Common patterns for all CLIs
└── <cli_name>/
    ├── README.md                # Navigation guide for this CLI
    ├── design.md                # Main overview with quick reference
    ├── <command>_design.md      # Detailed design for each command group
    └── ...
```

**Example for ADO CLI:**
```
docs/ado/
├── README.md              # ADO CLI documentation index
├── design.md              # Overview of all ADO commands
├── config_design.md       # All 'ado config' commands
├── repo_design.md         # All 'ado repo' commands
└── workitem_design.md     # All 'ado workitem' commands
```

**Benefits:**
- Easy to find all commands within a command group
- Clear separation of concerns
- Easier to maintain and update
- Better navigation for developers

## Best Practices and Key Patterns

### Critical Rules (DO NOT SKIP)

**1. Always use Poetry for dependency management**
- Never use `pip install` - always use `poetry add`
- Run `poetry lock` after any dependency changes
- Commit both `pyproject.toml` and `poetry.lock` together

**2. Always check if documents need updates after implementation**
- Review design docs for outdated command syntax, class names, function locations
- Update docs to match actual implementation (not just planned design)
- This is required, not optional - treat it like writing tests

**3. Write documentation for experienced developers and AI**
- Be concise - skip obvious explanations and redundant examples
- Focus on what's unique to this implementation
- Assume readers understand basic programming concepts

### Configuration Management
1. **Use configuration classes for validation** - Centralize error handling in properties
2. **Provide helpful error messages** - Guide users to fix configuration issues
3. **Use defaults where appropriate** - e.g., `server` defaults to `https://dev.azure.com`
4. **Preserve existing values** - When updating config, merge with existing data

### CLI Design
1. **Keep CLI code concise** - Delegate logic to common modules and config classes
2. **Use meaningful aliases** - e.g., `wi` for `workitem` for frequently used commands
3. **Validate early** - Check requirements before performing operations
4. **Provide clear error messages** - Include suggested fixes in error output

### Code Organization
1. **Segregation of duties** - CLI defines structure, common modules implement logic
2. **Single responsibility** - Each function/class has one clear purpose
3. **Reusability** - Common modules can be shared across CLIs
4. **Testability** - Business logic can be tested independently

### Testing Strategy
1. **Integration tests first** - Test complete user workflows
2. **Mock external dependencies** - File system, git, web browser, etc.
3. **Test error cases** - Missing config, invalid input, edge cases
4. **Organize by command groups** - e.g., `test_config_set.py`, `test_workitem_browse.py`

### Documentation Discipline
1. **Write for experienced developers and AI** - Be concise, assume knowledge
   - Skip obvious explanations (e.g., "reads config, merges, writes back")
   - Avoid redundant examples showing the same concept multiple ways
   - Focus on what's unique to this implementation, not general programming
   - Remove verbose step-by-step walkthroughs
   - Example: "Merges with existing config" not "1. Read config 2. Merge values 3. Write config"
2. **Update docs with code changes** - Keep documentation synchronized with implementation
3. **Check after implementation** - Review docs for outdated info (command syntax, class names, function locations)
4. **Include minimal code examples** - Show actual usage patterns, not full implementations
5. **Document the 'why'** - Explain benefits and trade-offs, not just the 'what'
6. **Cross-reference** - Link related documents together

**Documentation Style Guidelines:**
- ✅ **DO**: Focus on command syntax, options, configuration keys, key implementation components
- ✅ **DO**: Show brief examples demonstrating actual usage
- ✅ **DO**: Document defaults, exit codes, and error behaviors concisely
- ❌ **DON'T**: Include full implementation code listings (that's what the source code is for)
- ❌ **DON'T**: Show multiple redundant output format examples
- ❌ **DON'T**: Explain obvious behaviors step-by-step
- ❌ **DON'T**: List every possible field/property when "any field from X object" suffices

**Target audience**: AI agents and experienced developers who understand:
- Basic programming concepts (loops, conditionals, error handling)
- Common patterns (config management, CLI frameworks, testing)
- Standard library operations (file I/O, JSON parsing, etc.)

## Continuous Integration

GitHub Actions workflow (`.github/workflows/test.yml`) runs automatically on all branches:
- Sets up Python 3.13.2
- Installs Poetry
- Caches dependencies for faster runs
- Runs full test suite with pytest
- Ensures all tests pass before merging
