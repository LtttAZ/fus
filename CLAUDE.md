# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project named "fus" using Poetry for dependency management. The project requires Python 3.13.2 exactly.

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
