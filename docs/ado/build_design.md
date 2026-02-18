# ADO Build Commands

## Commands

### build list

Lists recent CI/CD builds for a specific repository with optional interactive opening.

```bash
ado build list --repo-name <name> [--top N]
```

**Options**:
- `--repo-name <name>` - Repository name (required, resolved to GUID via local cache)
- `--top N` - Maximum builds to return; overrides `build.top` config if specified (default: uses `build.top` config, which defaults to 50)

**Requirements**: `org`, `project` in config; `ADO_PAT` env var; repository must exist in local cache (populate with `ado repo list`)

**Configuration**:
```bash
ado config set --build.columns <fields>        # default: id,build_number,status,result,definition.name,source_branch,queue_time,finish_time
ado config set --build.column-names <names>    # default: Build ID,Number,Status,Result,Pipeline,Branch,Queued,Finished
ado config set --build.open true|false         # default: true
ado config set --build.top <N>                 # default: 50
```

**Field access**: Supports dot notation for nested fields (e.g., `definition.name`).

**Available fields**: Any Build API field: `id`, `build_number`, `status`, `result`, `reason`, `priority`, `definition.name`, `definition.id`, `source_branch`, `source_version`, `queue_time`, `start_time`, `finish_time`, `controller.id`, `requested_by.display_name`, etc.

**Output**: Rich table with auto-incrementing `#` column + configured columns. DateTime fields formatted as `YYYY-MM-DD HH:MM`. Null values displayed as `—`.

**Interactive Open**: After displaying the table, if open is enabled (via `build.open` config, default: true):
- Prompts user to enter a build number from the `#` column
- Validates the input (must be a valid 1-based index within range)
- Opens the selected build's results page in the default browser
- Press Enter to skip without opening

**Repo Resolution**: Repository name is resolved to GUID via local SQLite cache (`~/.fus/ado.db`). If not found:
- Error message includes the repository name and suggests running `ado repo list` first
- Exit code: 1

**Exit codes**: 0 (success), 1 (repo not found in cache, config missing, PAT not set, auth failed, API error)

**Example**:
```bash
ado config set --org myorg --project myproject
export ADO_PAT="token"
ado repo list                                  # Cache repo names locally

# List builds for a repository
ado build list --repo-name my-repo            # Shows last 50 builds

# Limit results
ado build list --repo-name my-repo --top 10   # Show only 10 most recent

# Custom columns
ado config set --build.columns id,build_number,status,result,definition.name
ado config set --build.column-names "ID,Build #,Status,Result,Pipeline"
ado build list --repo-name my-repo
```

## Implementation

**Key Components**:
- `BuildConfig` - Build-specific configuration class in `src/common/ado_config.py`, mirrors `RepoConfig` with properties for `columns`, `column_names`, `open`, `top`
- `AdoClient.list_builds()` - Azure DevOps Build API wrapper method that accepts repo_id and top parameter
- `build_ado_build_url()` in `src/common/ado_utils.py` - Constructs build results URL
- `get_nested_value(obj, field_path)` - Existing utility for dot-notation field access
- Rich table display with Console(width=200)

**Config Extension**:
- `get_default_config()` now includes `build` section with default columns/column-names/open/top
- `config set` command extended with `--build.columns`, `--build.column-names`, `--build.open`, `--build.top` options

**Error Handling**:
- Repo not found: Check cache via `ado_repo_db.get_id_by_name()`, exit 1 if None
- API errors: Caught as `AdoClientError`, displayed to user, exit 1
- Auth errors: Caught as `AdoAuthError`, displayed to user, exit 1

**Dependencies**: `azure-devops` SDK (already used for Git operations), `rich` (already used for tables), `src.common.ado_client`, `src.common.ado_exceptions`, `src.common.ado_repo_db`, `webbrowser` (stdlib)

**Database Integration**: Leverages existing SQLite repo cache populated by `ado repo list`
