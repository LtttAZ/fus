# ADO Repo Commands

## Commands

### repo browse

Opens current git repo in browser.

```bash
ado repo browse [--branch <branch>]
```

**Behavior**: Parses origin remote URL, constructs ADO URL, opens browser
**Exit codes**: 0 (success), 1 (not in git repo, no origin, invalid URL)

### repo list

Lists all repositories in the configured project with optional pattern filtering and interactive opening.

```bash
ado repo list [--pattern <pattern>] [--open]
```

**Options**:
- `--pattern <pattern>` (alias: `--patt`) - Filter repositories by name using glob pattern (e.g., `my-*`, `*-repo`, `proj-?`)
- `--open` - After displaying the table, prompt to open a repository in the browser by entering its number from the `#` column

**Requirements**: `org`, `project` in config; `ADO_PAT` env var

**Configuration**:
```bash
ado config set --repo.columns <fields>        # default: id,name
ado config set --repo.column-names <names>    # default: repo_id,repo_name
```

**Field access**: Supports dot notation for nested fields (e.g., `project.name`). Automatically parses JSON strings when traversing.

**Available fields**: Any `GitRepository` field: `name`, `id`, `remote_url`, `ssh_url`, `web_url`, `default_branch`, `size`, `project.name`, `project.id`, etc.

**Filtering**: Client-side filtering using Python's `fnmatch` module. Supports standard glob patterns:
- `*` - matches any sequence of characters
- `?` - matches any single character
- `[seq]` - matches any character in seq
- `[!seq]` - matches any character not in seq

**Interactive Open**: When `--open` is used, after displaying the table:
- Prompts user to enter a repository number from the `#` column
- Validates the input (must be a valid number within range)
- Opens the selected repository's `web_url` in the default browser
- Press Ctrl+C to cancel without opening

**Output**: Rich table with auto-incrementing `#` column + configured columns

**Exit codes**: 0 (success), 1 (config missing, PAT not set, auth failed, invalid field, invalid repo number, column name count mismatch)

**Example**:
```bash
ado config set --org myorg --project myproject
export ADO_PAT="token"
ado repo list

# Filter by pattern
ado repo list --pattern "my-*"        # repos starting with "my-"
ado repo list --patt "*-service"      # repos ending with "-service"
ado repo list --pattern "api-?"       # repos like "api-1", "api-2", etc.

# Interactive open
ado repo list --open                  # Display table, then prompt for repo number
ado repo list --pattern "api-*" --open  # Filter and open

# Custom columns
ado config set --repo.columns name,web_url,project.name
ado config set --repo.column-names Repository,URL,Project
```

## Implementation

**Key Components**:
- `AdoClient.list_repos()` - Fetches repos via Azure DevOps SDK
- `fnmatch.fnmatch()` - Client-side filtering using glob patterns
- `get_nested_value(obj, field_path)` in `src.common.ado_utils` - Handles dot notation with JSON parsing
- `config.repo.columns` / `config.repo.column_names` - `RepoConfig` properties returning `list[str]` with defaults applied; `column_names` raises error on count mismatch
- Rich table with `Console(width=200)` and `no_wrap=True` columns

**Error handling**: Config validation via `AdoConfig` properties, field access errors caught and reported

**URL parsing**: `parse_ado_remote_url()` handles HTTPS (with/without username), SSH, and on-premises formats

**Dependencies**: `azure-devops`, `rich`, `fnmatch`, `src.common.ado_client`, `src.common.ado_exceptions`
