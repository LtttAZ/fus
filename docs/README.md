# Documentation

This directory contains design documents and technical documentation for the fus CLI tools project.

## General Documentation

- **[cli_design.md](cli_design.md)** - Common design patterns and technical guidelines for all CLI tools

## CLI-Specific Documentation

### ADO (Azure DevOps) CLI
- **[ado/](ado/)** - Design documentation for the ADO CLI
  - [design.md](ado/design.md) - Main design document with all commands
  - [repo_browse_design.md](ado/repo_browse_design.md) - Repository browsing feature
  - [workitem_browse_design.md](ado/workitem_browse_design.md) - Work item browsing feature

## Documentation Structure

Each CLI tool should have its own subdirectory with:
- `design.md` - Main design document covering all commands and features
- `<feature>_design.md` - Optional detailed design documents for complex features
- `README.md` - Quick reference and navigation guide

## Development Process

This project follows a document-first approach:

1. **Design Phase**: Create or update design documents before implementation
2. **Review**: Design documents are reviewed and approved
3. **Test Phase**: Write integration tests based on the approved design
4. **Implementation**: Implement features to satisfy the tests

See [../CLAUDE.md](../CLAUDE.md) for detailed development workflow.
