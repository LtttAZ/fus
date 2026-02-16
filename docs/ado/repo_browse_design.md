# ADO Repo Browse Command - Design Document

## Overview

The `ado repo browse` command opens the current git repository's Azure DevOps URL in the default web browser.

## Command Signature

```bash
ado repo browse [--branch=<branch>]
```

### Options

- `--branch`: Optional branch name to browse. If not provided, uses the current git branch.

## Behavior

### URL Construction

The command constructs an Azure DevOps repository URL using:

1. **Organization, Project, Repo Name**: Extracted from the git remote URL
2. **Branch**: Uses `--branch` option if provided, otherwise uses current git branch from `get_current_branch()`

### Git Remote URL Parsing

Azure DevOps remote URLs follow these formats:

**HTTPS Format:**
```
https://dev.azure.com/{org}/{project}/_git/{repo}
https://{org}@dev.azure.com/{org}/{project}/_git/{repo}
```

**SSH Format:**
```
git@ssh.dev.azure.com:v3/{org}/{project}/{repo}
```

**On-Premises Format:**
```
https://{server}/{org}/{project}/_git/{repo}
```

The parser should extract `org`, `project`, and `repo` from these formats.

### Azure DevOps URL Format

The browser will open:
```
https://dev.azure.com/{org}/{project}/_git/{repo}?version=GB{branch}
```

If no branch is specified (neither via option nor current branch), omit the `?version=GB{branch}` parameter.

## Error Handling

### Not in a Git Repository
**Condition**: Current directory is not within a git repository
**Message**: `Error: Not in a git repository`
**Exit Code**: 1

### No Remote Found
**Condition**: Git repository has no remote named "origin"
**Message**: `Error: No remote 'origin' found`
**Exit Code**: 1

### Invalid Remote URL Format
**Condition**: Remote URL cannot be parsed as an Azure DevOps URL
**Message**: `Error: Remote URL is not a valid Azure DevOps repository URL`
**Exit Code**: 1

### Cannot Determine Branch
**Condition**: No `--branch` option provided and cannot get current branch
**Message**: `Error: Cannot determine current branch`
**Exit Code**: 1

## Implementation Notes

### Dependencies
- `src.common.git_utils`: For `is_git_repository()`, `get_remote_url()`, `get_current_branch()`
- `webbrowser` module: For opening URLs in default browser
- URL parsing logic: To extract org/project/repo from remote URL

### URL Parser
Create a function in `src.common.ado_utils.py`:
```python
def parse_ado_remote_url(remote_url: str) -> Optional[tuple[str, str, str]]:
    """
    Parse Azure DevOps remote URL to extract org, project, and repo.

    Returns:
        Tuple of (org, project, repo) if valid ADO URL, None otherwise.
    """
```

### URL Builder
Create a function in `src.common.ado_utils.py`:
```python
def build_ado_repo_url(org: str, project: str, repo: str, branch: Optional[str] = None) -> str:
    """
    Build Azure DevOps repository URL.

    Args:
        org: Organization name
        project: Project name
        repo: Repository name
        branch: Optional branch name

    Returns:
        Full Azure DevOps repository URL
    """
```

## Success Output

When successful, display:
```
Opening: https://dev.azure.com/{org}/{project}/_git/{repo}?version=GB{branch}
```

Then open the URL in the default browser.
