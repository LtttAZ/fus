# ADO CLI Documentation

This directory contains design documentation for the ADO (Azure DevOps) CLI tool.

## Overview

The ADO CLI provides commands for interacting with Azure DevOps from the command line. It supports configuration management, repository browsing, and work item operations.

## Documentation Files

### Main Design Document
- **[design.md](design.md)** - Overview of all ADO CLI commands with quick reference

### Command-Specific Design Documents
- **[config_design.md](config_design.md)** - Configuration commands (`ado config`)
- **[repo_design.md](repo_design.md)** - Repository commands (`ado repo`)
- **[workitem_design.md](workitem_design.md)** - Work item commands (`ado workitem`, `ado wi`)

### API Client Design
- **[client_design.md](client_design.md)** - Azure DevOps REST API client for programmatic access

## Quick Reference

### Configuration
```bash
ado config set --project <project> --org <org> [--server <server>]
```

### Repository Commands
```bash
ado repo browse [--branch <branch>]
```

### Work Item Commands
```bash
ado workitem browse --id <id>
ado wi browse --id <id>           # Short alias
```

## Implementation

The ADO CLI follows the project's [CLI design patterns](../cli_design.md) with:
- CLI definitions in `src/cli/ado.py`
- Business logic in `src/common/ado_config.py`, `src/common/ado_utils.py`
- Git utilities in `src/common/git_utils.py`
- Integration tests in `tests/ado/`
