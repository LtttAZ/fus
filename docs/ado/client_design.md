# ADO Client - Design Document

## Overview

The `AdoClient` is a Python client that wraps the official [Microsoft Azure DevOps Python API](https://github.com/microsoft/azure-devops-python-api). It provides programmatic access to Azure DevOps resources, starting with repository operations.

**Purpose:**
- Provide a simplified, opinionated interface to Azure DevOps API using the official SDK
- Handle authentication and connection setup using Personal Access Tokens (PAT)
- Centralize error handling and configuration management
- Enable CLI commands to interact with Azure DevOps beyond just opening URLs

## Initial Scope

**Version 1.0 Focus:** Repository operations only
- List repositories in a project
- Get repository details

**Future expansion:** Work items, pull requests, pipelines, etc.

## Authentication

### Personal Access Token (PAT)

The client uses Azure DevOps Personal Access Tokens for authentication.

**PAT Storage:**
- PAT is provided via the `ADO_PAT` environment variable
- PAT is NOT stored in configuration files (more secure)
- Required only for API operations (browse commands don't need it)

**Setting the PAT:**

Unix/Linux/macOS:
```bash
export ADO_PAT="your-personal-access-token-here"
```

Windows (Command Prompt):
```cmd
set ADO_PAT=your-personal-access-token-here
```

Windows (PowerShell):
```powershell
$env:ADO_PAT="your-personal-access-token-here"
```

**Permanent Configuration:**

Add to shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export ADO_PAT="your-personal-access-token-here"
```

**Configuration Example (no PAT in file):**
```yaml
org: MyOrganization
project: MyProject
server: https://dev.azure.com
# PAT comes from ADO_PAT environment variable
```

**Security Notes:**
- PAT stored in environment variable (not in config file)
- Prevents accidental commit to version control
- Can use different PATs for different shells/environments
- PAT should have minimal required scopes (Code: Read for repository operations)

### Authentication Method

The Azure DevOps Python API uses `BasicAuthentication` credentials with PAT:

```python
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

# Create credentials
credentials = BasicAuthentication('', pat_token)

# Create connection
connection = Connection(base_url=organization_url, creds=credentials)
```

**Organization URL format:**
- Cloud: `https://dev.azure.com/{org}`
- On-premises: `{server}/{org}`

## Client Design

### Class Structure

```python
from typing import Optional, List
from azure.devops.connection import Connection
from azure.devops.v7_0.git.git_client import GitClient
from azure.devops.v7_0.git.models import GitRepository
from msrest.authentication import BasicAuthentication

class AdoClient:
    """Client for interacting with Azure DevOps API using official SDK."""

    def __init__(self, config: Optional[AdoConfig] = None):
        """
        Initialize ADO client.

        Args:
            config: AdoConfig instance. If None, loads from default location.
        """
        self.config = config or AdoConfig()
        self._connection = self._create_connection()
        self._git_client = self._connection.clients.get_git_client()

    def _create_connection(self) -> Connection:
        """Create Azure DevOps connection with authentication."""
        # Build organization URL from server and org
        org_url = f"{self.config.server}/{self.config.org}"

        # Create credentials
        credentials = BasicAuthentication('', self.config.pat)

        # Create and return connection
        return Connection(base_url=org_url, creds=credentials)

    def list_repos(self, project: Optional[str] = None) -> List[GitRepository]:
        """
        List all repositories in a project.

        Args:
            project: Project name. If None, uses configured project.

        Returns:
            List of GitRepository objects

        Raises:
            AdoClientError: If API request fails
            AdoAuthError: If authentication fails
            AdoNotFoundError: If project not found
        """

    def get_repo(self, repo_id: str, project: Optional[str] = None) -> GitRepository:
        """
        Get details of a specific repository.

        Args:
            repo_id: Repository ID or name
            project: Project name. If None, uses configured project.

        Returns:
            GitRepository object

        Raises:
            AdoClientError: If API request fails
            AdoAuthError: If authentication fails
            AdoNotFoundError: If repository not found
        """
```

### Error Handling

**Custom Exceptions:**

```python
class AdoClientError(Exception):
    """Base exception for ADO client errors."""
    pass

class AdoAuthError(AdoClientError):
    """Authentication error (401)."""
    pass

class AdoNotFoundError(AdoClientError):
    """Resource not found (404)."""
    pass

class AdoConfigError(AdoClientError):
    """Configuration error (missing PAT, org, project, etc.)."""
    pass
```

**Error Messages:**
- `AdoAuthError`: "Authentication failed. Check your ADO_PAT environment variable."
- `AdoNotFoundError`: "Resource not found: {url}"
- `AdoConfigError`: "ADO_PAT environment variable not set. Set it with: export ADO_PAT='your-token'"

### Configuration Validation

The client should validate required configuration before making API calls:

**Required for API operations:**
- `server`: Server URL (defaults to `https://dev.azure.com`)
- `org`: Organization name
- `project`: Project name
- `ADO_PAT`: Environment variable with Personal Access Token

**Validation approach:**
- Use `AdoConfig` class for server, org, project validation
- Read PAT from environment variable with validation

## Implementation Details

### Dependencies

**Azure DevOps Python API:**
- Package: `azure-devops`
- Repository: https://github.com/microsoft/azure-devops-python-api
- Documentation: https://github.com/microsoft/azure-devops-python-api/blob/dev/README.md

Add to `pyproject.toml`:
```toml
[tool.poetry.dependencies]
azure-devops = "^7.1.0"
```

**Key SDK Components:**
- `azure.devops.connection.Connection` - Connection management
- `msrest.authentication.BasicAuthentication` - PAT authentication
- `azure.devops.v7_0.git.git_client.GitClient` - Git operations
- `azure.devops.v7_0.git.models.GitRepository` - Repository model

### File Structure

```
src/common/
├── ado_client.py        # AdoClient class
├── ado_exceptions.py    # Custom exception classes
└── ado_config.py        # Updated with PAT property
```

### AdoConfig Enhancement

Add PAT support to existing `AdoConfig` class by reading from environment variable:

```python
import os

class AdoConfig:
    """ADO configuration with validation and error handling."""

    # ... existing properties ...

    @property
    def pat(self) -> str:
        """Get Personal Access Token from environment variable, exits with error if not set."""
        value = os.getenv("ADO_PAT")
        if not value:
            typer.echo("Error: ADO_PAT environment variable not set.")
            typer.echo("Set it with: export ADO_PAT='your-personal-access-token'")
            raise typer.Exit(code=1)
        return value
```

**Benefits:**
- More secure than config file storage
- Prevents accidental commits of credentials
- Standard practice for API credentials
- Easy to rotate tokens without changing config files

### Connection Setup

```python
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

def _create_connection(self) -> Connection:
    """Create Azure DevOps connection with authentication."""
    # Build organization URL
    org_url = f"{self.config.server}/{self.config.org}"

    # Create credentials with PAT
    credentials = BasicAuthentication('', self.config.pat)

    # Create connection
    connection = Connection(base_url=org_url, creds=credentials)

    return connection
```

**Note:** The organization URL should NOT include the project - that's specified per-operation.

### Repository Operations Implementation

```python
from azure.devops.v7_0.git.models import GitRepository
from typing import List, Optional

def list_repos(self, project: Optional[str] = None) -> List[GitRepository]:
    """List all repositories in a project."""
    project_name = project or self.config.project

    try:
        repos = self._git_client.get_repositories(project_name)
        return repos
    except Exception as e:
        # SDK exceptions need to be wrapped
        self._handle_sdk_exception(e)

def get_repo(self, repo_id: str, project: Optional[str] = None) -> GitRepository:
    """Get a specific repository."""
    project_name = project or self.config.project

    try:
        repo = self._git_client.get_repository(
            project=project_name,
            repository_id=repo_id
        )
        return repo
    except Exception as e:
        self._handle_sdk_exception(e)

def _handle_sdk_exception(self, exception: Exception) -> None:
    """Convert SDK exceptions to our custom exceptions."""
    error_msg = str(exception)

    if "401" in error_msg or "Unauthorized" in error_msg:
        raise AdoAuthError("Authentication failed. Check your ADO_PAT environment variable.")
    elif "404" in error_msg or "not found" in error_msg.lower():
        raise AdoNotFoundError(f"Resource not found: {error_msg}")
    else:
        raise AdoClientError(f"Azure DevOps API error: {error_msg}")
```

## Usage Example

### CLI Command Example

```python
# src/cli/ado.py
@repo_app.command("list")
def repo_list() -> None:
    """List all repositories in the project."""
    from src.common.ado_client import AdoClient
    from src.common.ado_exceptions import AdoClientError

    try:
        # ADO_PAT environment variable must be set
        client = AdoClient()
        repos = client.list_repos()

        for repo in repos:
            typer.echo(f"{repo.name} - {repo.remote_url}")

    except AdoClientError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)
```

**Usage:**
```bash
# Set PAT first
export ADO_PAT="your-token"

# Then run command
ado repo list
```

### Python API Example

```python
import os
from src.common.ado_client import AdoClient
from src.common.ado_config import AdoConfig

# Ensure ADO_PAT is set
if not os.getenv("ADO_PAT"):
    raise ValueError("ADO_PAT environment variable must be set")

# Using default config
client = AdoClient()
repos = client.list_repos()

# Using custom config
config = AdoConfig()
client = AdoClient(config=config)
repos = client.list_repos()

# Access repository properties
for repo in repos:
    print(f"Name: {repo.name}")
    print(f"ID: {repo.id}")
    print(f"Remote URL: {repo.remote_url}")
    print(f"Default Branch: {repo.default_branch}")
    print(f"Web URL: {repo.web_url}")
    print("---")

# Get specific repository
repo = client.get_repo("my-repo-name")
print(f"Repository: {repo.name} ({repo.id})")
```

### GitRepository Object Properties

The SDK returns `GitRepository` objects with these key properties:

```python
repo.id                 # Repository GUID
repo.name              # Repository name
repo.url               # API URL
repo.remote_url        # Git clone URL (HTTPS)
repo.ssh_url           # Git clone URL (SSH)
repo.web_url           # Browser URL
repo.default_branch    # Default branch ref (e.g., "refs/heads/main")
repo.project.name      # Project name
repo.project.id        # Project GUID
repo.size              # Repository size in bytes
```

## Testing Strategy

### Unit Tests

Test the client with mocked SDK responses and environment variables:

```python
# tests/common/test_ado_client.py
import os
from unittest.mock import Mock, patch
from azure.devops.v7_0.git.models import GitRepository

class TestAdoClient:
    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    def test_list_repos_success(self, mock_git_client):
        """Test successful repository listing."""
        # Mock GitRepository objects
        mock_repo = Mock(spec=GitRepository)
        mock_repo.name = "test-repo"
        mock_repo.id = "123"
        mock_repo.remote_url = "https://dev.azure.com/org/proj/_git/test-repo"

        mock_git_client.get_repositories.return_value = [mock_repo]

        # Test
        client = AdoClient()
        repos = client.list_repos()

        assert len(repos) == 1
        assert repos[0].name == "test-repo"
        mock_git_client.get_repositories.assert_called_once()

    def test_missing_pat_environment_variable(self):
        """Test error when ADO_PAT is not set."""
        # Ensure ADO_PAT is not set
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(typer.Exit):
                config = AdoConfig()
                _ = config.pat

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    def test_list_repos_auth_error(self, mock_connection):
        """Test authentication failure."""
        # Mock SDK exception for 401
        mock_connection.side_effect = Exception("401 Unauthorized")

        # Verify AdoAuthError is raised
        with pytest.raises(AdoAuthError):
            client = AdoClient()
            client.list_repos()

    @patch.dict(os.environ, {"ADO_PAT": "test-token"})
    def test_list_repos_not_found(self, mock_git_client):
        """Test project not found."""
        # Mock SDK exception for 404
        mock_git_client.get_repositories.side_effect = Exception("404 Project not found")

        # Verify AdoNotFoundError is raised
        with pytest.raises(AdoNotFoundError):
            client = AdoClient()
            client.list_repos()
```

### Integration Tests

Test with actual Azure DevOps API (requires ADO_PAT environment variable):

```python
# tests/integration/test_ado_client_integration.py
import os
import pytest

@pytest.mark.integration
class TestAdoClientIntegration:
    def test_list_repos_real_api(self):
        """Test listing repos with real API (requires ADO_PAT env var)."""
        # Skip if ADO_PAT not set
        if not os.getenv("ADO_PAT"):
            pytest.skip("ADO_PAT environment variable not set")

        # Make real API call
        client = AdoClient()
        repos = client.list_repos()

        # Verify response structure
        assert isinstance(repos, list)
        if repos:
            assert hasattr(repos[0], 'name')
            assert hasattr(repos[0], 'id')
            assert hasattr(repos[0], 'remote_url')
```

## Environment Variable Setup

### Setting ADO_PAT

The PAT is configured via the `ADO_PAT` environment variable, not in the config file.

**For current session:**

Unix/Linux/macOS:
```bash
export ADO_PAT="your-personal-access-token"
```

Windows (Command Prompt):
```cmd
set ADO_PAT=your-personal-access-token
```

Windows (PowerShell):
```powershell
$env:ADO_PAT="your-personal-access-token"
```

**For permanent setup, add to shell profile:**

`~/.bashrc` or `~/.zshrc`:
```bash
# Azure DevOps PAT
export ADO_PAT="your-personal-access-token"
```

**Verification:**

Unix/Linux/macOS:
```bash
echo $ADO_PAT
```

Windows (Command Prompt):
```cmd
echo %ADO_PAT%
```

Windows (PowerShell):
```powershell
echo $env:ADO_PAT
```

**Security Best Practices:**
- Never commit PAT to version control
- Use different PATs for different projects/environments
- Rotate PATs regularly
- Use minimal required scopes (e.g., Code: Read for read-only operations)
- Consider using a secrets manager for team environments

## SDK Model Objects

The Azure DevOps Python SDK automatically deserializes JSON responses into Python model objects.

### GitRepository Model

The SDK returns `GitRepository` objects from `azure.devops.v7_0.git.models`:

**Key Properties:**
- `id` (str): Repository GUID
- `name` (str): Repository name
- `url` (str): API endpoint URL
- `remote_url` (str): Git clone URL (HTTPS)
- `ssh_url` (str): Git clone URL (SSH)
- `web_url` (str): Browser URL
- `default_branch` (str): Default branch reference
- `project` (TeamProjectReference): Project information
- `size` (int): Repository size in bytes

**Example raw API response** (for reference - SDK handles this):
```json
{
  "id": "2f3d611a-f012-4b39-b157-8db63f380226",
  "name": "my-repo",
  "url": "https://dev.azure.com/myorg/_apis/git/repositories/2f3d611a-f012-4b39-b157-8db63f380226",
  "project": {
    "id": "a7f897de-3e51-4f2c-9b6c-5e8b7f6e5d4c",
    "name": "MyProject",
    "state": "wellFormed"
  },
  "defaultBranch": "refs/heads/main",
  "remoteUrl": "https://dev.azure.com/myorg/MyProject/_git/my-repo",
  "sshUrl": "git@ssh.dev.azure.com:v3/myorg/MyProject/my-repo",
  "webUrl": "https://dev.azure.com/myorg/MyProject/_git/my-repo"
}
```

**SDK automatically converts** `snake_case` JSON keys to `PascalCase` properties and vice versa.

### Working with Model Objects

```python
# List repos returns List[GitRepository]
repos = client.list_repos()

for repo in repos:
    # Access properties directly
    print(repo.name)           # "my-repo"
    print(repo.remote_url)     # "https://dev.azure.com/..."
    print(repo.project.name)   # "MyProject"

# Get repo returns GitRepository
repo = client.get_repo("my-repo")
print(f"{repo.name} default branch: {repo.default_branch}")
```

## Future Enhancements

**Version 2.0:**
- Work item operations (get, create, update)
- Pull request operations
- Branch operations
- Pipeline operations

**Authentication:**
- OAuth support
- Azure CLI credential integration
- Service principal authentication

**Features:**
- Pagination support for large result sets
- Caching for frequently accessed data
- Retry logic with exponential backoff
- Response models using Pydantic

## References

**Azure DevOps Python API (SDK):**
- GitHub Repository: https://github.com/microsoft/azure-devops-python-api
- README: https://github.com/microsoft/azure-devops-python-api/blob/dev/README.md
- PyPI Package: https://pypi.org/project/azure-devops/
- Samples: https://github.com/microsoft/azure-devops-python-samples

**Azure DevOps REST API Documentation:**
- Overview: https://learn.microsoft.com/en-us/rest/api/azure/devops/
- Git API: https://learn.microsoft.com/en-us/rest/api/azure/devops/git/
- Authentication: https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate

**SDK Version:**
- Using SDK version `7.x` which supports API version 7.0+
- SDK handles API versioning automatically
