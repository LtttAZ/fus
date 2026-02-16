# ADO Config Commands

**Cross-platform**: Runs on Windows (Command Prompt, PowerShell, Git Bash), Linux, macOS.

**Configuration file location** (via `platformdirs.user_config_dir("fus")`):
- **Windows**: `%LOCALAPPDATA%\fus\ado.yaml`
- **Linux**: `~/.config/fus/ado.yaml`
- **macOS**: `~/Library/Application Support/fus/ado.yaml`

## Commands

### config list

Lists all config values alphabetically. Default `server: https://dev.azure.com` shown if not configured.

```bash
ado config list
# Output: key: value (sorted alphabetically)
```

### config set

```bash
# Top-level config
ado config set --project <project> --org <org> --server <server>

# Repo-specific config
ado config set --repo-columns <fields> --repo-column-names <display-names>

# Examples
ado config set --org MyOrg --project MyProject
ado config set --repo-columns id,name,web_url --repo-column-names "ID,Name,URL"
```

**Behavior**: Merges with existing config (preserves unspecified values). Requires at least one option.

**Exit codes**: 0 (success), 1 (no options or error)

## Configuration Keys

```yaml
org: MyOrg
project: MyProject
server: https://dev.azure.com  # default
repo:
  columns: id,name  # default
  column-names: repo_id,repo_name  # default
```

## Implementation

### Config Classes

**AdoConfig** - Main config with validation:
```python
class AdoConfig:
    @property
    def server(self) -> str:  # defaults to https://dev.azure.com
    @property
    def org(self) -> str:  # exits with error if not set
    @property
    def project(self) -> str:  # exits with error if not set
    @property
    def pat(self) -> str:  # from ADO_PAT env var, exits if not set
    @property
    def repo(self) -> RepoConfig:  # lazy-initialized
```

**RepoConfig** - Repo-specific config:
```python
class RepoConfig:
    @property
    def columns(self) -> str | None
    @property
    def column_names(self) -> str | None
```

### Helper Functions

**set_nested_value(config, key, value)** - Handles dot notation for nested config keys

**Dependencies**: `platformdirs`, `PyYAML`, `typer`

**Functions**: `get_config_path()`, `read_config()`, `write_config()` in `src.common.ado_config`
