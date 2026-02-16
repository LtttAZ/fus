"""Integration tests for ado repo browse command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock


@pytest.fixture
def runner():
    """Create a CliRunner for testing."""
    return CliRunner()


class TestRepoBrowseSuccess:
    """Test successful repo browse operations."""

    def test_browse_with_current_branch(self, runner):
        """Test browsing with current branch (no --branch option)."""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://dev.azure.com/myorg/myproject/_git/myrepo'), \
             patch('src.cli.ado.get_current_branch', return_value='main'), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 0
            assert "Opening: https://dev.azure.com/myorg/myproject/_git/myrepo?version=GBmain" in result.stdout
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/myproject/_git/myrepo?version=GBmain")

    def test_browse_with_branch_option(self, runner):
        """Test browsing with --branch option."""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://dev.azure.com/myorg/myproject/_git/myrepo'), \
             patch('src.cli.ado.get_current_branch', return_value='main'), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse", "--branch", "feature/test"])

            assert result.exit_code == 0
            assert "Opening: https://dev.azure.com/myorg/myproject/_git/myrepo?version=GBfeature/test" in result.stdout
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/myproject/_git/myrepo?version=GBfeature/test")

    def test_browse_without_branch(self, runner):
        """Test browsing when no branch can be determined (omit version parameter)."""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://dev.azure.com/myorg/myproject/_git/myrepo'), \
             patch('src.cli.ado.get_current_branch', return_value=None), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 0
            assert "Opening: https://dev.azure.com/myorg/myproject/_git/myrepo" in result.stdout
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/myproject/_git/myrepo")


class TestRepoBrowseUrlFormats:
    """Test parsing different Azure DevOps URL formats."""

    def test_https_format_basic(self, runner):
        """Test HTTPS format: https://dev.azure.com/{org}/{project}/_git/{repo}"""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://dev.azure.com/contoso/MyProject/_git/MyRepo'), \
             patch('src.cli.ado.get_current_branch', return_value='develop'), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 0
            mock_open.assert_called_once_with("https://dev.azure.com/contoso/MyProject/_git/MyRepo?version=GBdevelop")

    def test_https_format_with_username(self, runner):
        """Test HTTPS format with username: https://{org}@dev.azure.com/{org}/{project}/_git/{repo}"""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://contoso@dev.azure.com/contoso/MyProject/_git/MyRepo'), \
             patch('src.cli.ado.get_current_branch', return_value='main'), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 0
            mock_open.assert_called_once_with("https://dev.azure.com/contoso/MyProject/_git/MyRepo?version=GBmain")

    def test_ssh_format(self, runner):
        """Test SSH format: git@ssh.dev.azure.com:v3/{org}/{project}/{repo}"""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='git@ssh.dev.azure.com:v3/contoso/MyProject/MyRepo'), \
             patch('src.cli.ado.get_current_branch', return_value='main'), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 0
            mock_open.assert_called_once_with("https://dev.azure.com/contoso/MyProject/_git/MyRepo?version=GBmain")

    def test_onpremises_format(self, runner):
        """Test on-premises format: https://{server}/{org}/{project}/_git/{repo}"""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://tfs.company.com/contoso/MyProject/_git/MyRepo'), \
             patch('src.cli.ado.get_current_branch', return_value='main'), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 0
            # On-premises should use the original server, not dev.azure.com
            mock_open.assert_called_once_with("https://tfs.company.com/contoso/MyProject/_git/MyRepo?version=GBmain")


class TestRepoBrowseErrors:
    """Test error handling."""

    def test_not_in_git_repository(self, runner):
        """Test error when not in a git repository."""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=False):
            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 1
            assert "Error: Not in a git repository" in result.stdout

    def test_no_origin_remote(self, runner):
        """Test error when no origin remote found."""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value=None):

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 1
            assert "Error: No remote 'origin' found" in result.stdout

    def test_invalid_ado_url(self, runner):
        """Test error when remote URL is not a valid Azure DevOps URL."""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://github.com/user/repo.git'):

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 1
            assert "Error: Remote URL is not a valid Azure DevOps repository URL" in result.stdout


class TestRepoBrowseEdgeCases:
    """Test edge cases."""

    def test_repo_name_with_dots(self, runner):
        """Test repository names containing dots."""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://dev.azure.com/myorg/myproject/_git/my.repo.name'), \
             patch('src.cli.ado.get_current_branch', return_value='main'), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 0
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/myproject/_git/my.repo.name?version=GBmain")

    def test_branch_with_slashes(self, runner):
        """Test branch names containing slashes (e.g., feature/new-feature)."""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://dev.azure.com/myorg/myproject/_git/myrepo'), \
             patch('src.cli.ado.get_current_branch', return_value='feature/add-new-feature'), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 0
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/myproject/_git/myrepo?version=GBfeature/add-new-feature")

    def test_project_name_with_spaces(self, runner):
        """Test project names with spaces (URL encoded in remote)."""
        from src.cli.ado import app

        with patch('src.cli.ado.is_git_repository', return_value=True), \
             patch('src.cli.ado.get_remote_url', return_value='https://dev.azure.com/myorg/My%20Project/_git/myrepo'), \
             patch('src.cli.ado.get_current_branch', return_value='main'), \
             patch('src.cli.ado.webbrowser.open') as mock_open:

            result = runner.invoke(app, ["repo", "browse"])

            assert result.exit_code == 0
            # Should preserve URL encoding
            mock_open.assert_called_once_with("https://dev.azure.com/myorg/My%20Project/_git/myrepo?version=GBmain")
