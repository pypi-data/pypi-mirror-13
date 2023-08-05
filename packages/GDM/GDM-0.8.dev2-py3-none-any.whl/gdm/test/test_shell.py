"""Unit tests for the `shell` module."""
# pylint: disable=no-self-use

from unittest.mock import patch, Mock

import pytest

from gdm.common import CallException
from gdm.shell import call, ShellMixin, GitMixin


class TestCall:

    """Tests for interacting with the shell."""

    @patch('os.chdir')
    def test_cd(self, mock_chdir):
        """Verify directories are changed correctly."""
        call('cd', 'mock/dir')
        mock_chdir.assert_called_once_with('mock/dir')

    @patch('gdm.shell.Command')
    def test_other(self, mock_command):
        """Verify directories are changed correctly."""
        call('mock_program')
        mock_command.assert_called_once_with('mock_program')

    def test_other_error(self):
        """Verify program errors are handled."""
        with pytest.raises(SystemExit):
            call('git', '--invalid-git-argument')

    def test_other_error_uncaught(self):
        """Verify program errors can be left uncaught."""
        with pytest.raises(CallException):
            call('git', '--invalid-git-argument', catch=False)

    def test_other_error_ignored(self):
        """Verify program errors can be ignored."""
        call('git', '--invalid-git-argument', ignore=True)

    def test_other_capture(self):
        """Verify a program's output can be captured."""
        stdout = call('echo', 'Hello, world!\n', capture=True)
        assert "Hello, world!" == stdout


def assert_calls(mock_call, expected):
    """Confirm the expected list of calls matches the mock call."""
    __tracebackhide__ = True  # pylint: disable=unused-variable
    actual = [' '.join(args[0]) for args in mock_call.call_args_list]
    assert expected == actual


@patch('gdm.shell.call')
class TestShell:

    """Tests for calls to shell utilities."""

    shell = ShellMixin()

    def test_mkdir(self, mock_call):
        """Verify the commands to create directories."""
        self.shell.mkdir('mock/dir/path')
        assert_calls(mock_call, ["mkdir -p mock/dir/path"])

    def test_cd(self, mock_call):
        """Verify the commands to change directories."""
        self.shell.cd('mock/dir/path')
        assert_calls(mock_call, ["cd mock/dir/path"])

    @patch('os.path.isdir', Mock(return_value=True))
    def test_ln(self, mock_call):
        """Verify the commands to create symbolic links."""
        self.shell.ln('mock/target', 'mock/source')
        assert_calls(mock_call, ["ln -s mock/target mock/source"])

    @patch('os.path.isdir', Mock(return_value=False))
    def test_ln_missing_parent(self, mock_call):
        """Verify the commands to create symbolic links (missing parent)."""
        self.shell.ln('mock/target', 'mock/source')
        assert_calls(mock_call, ["mkdir -p mock",
                                 "ln -s mock/target mock/source"])

    def test_rm(self, mock_call):
        """Verify the commands to delete files/folders."""
        self.shell.rm('mock/dir/path')
        assert_calls(mock_call, ["rm -rf mock/dir/path"])


@patch('gdm.shell.call')
class TestGit:

    """Tests for calls to Git."""

    shell = GitMixin()

    @patch('os.path.isdir', Mock(return_value=False))
    def test_clone(self, mock_call):
        """Verify the commands to set up a new reference repository."""
        self.shell.git_clone('mock.git', 'mock/path', cache='cache')
        assert_calls(mock_call, [
            "git clone --mirror mock.git cache/mock.reference",
            "git clone --reference cache/mock.reference mock.git mock/path"])

    @patch('os.path.isdir', Mock(return_value=True))
    def test_clone_from_reference(self, mock_call):
        """Verify the commands to clone a Git repository from a reference."""
        self.shell.git_clone('mock.git', 'mock/path', cache='cache')
        assert_calls(mock_call, [
            "git clone --reference cache/mock.reference mock.git mock/path"])

    def test_fetch(self, mock_call):
        """Verify the commands to fetch from a Git repository."""
        self.shell.git_fetch('mock.git')
        assert_calls(mock_call, [
            "git remote rm origin",
            "git remote add origin mock.git",
            "git fetch --tags --force --prune origin",
        ])

    def test_fetch_rev(self, mock_call):
        """Verify the commands to fetch from a Git repository w/ rev."""
        self.shell.git_fetch('mock.git', 'mock-rev')
        assert_calls(mock_call, [
            "git remote rm origin",
            "git remote add origin mock.git",
            "git fetch --tags --force --prune origin mock-rev",
        ])

    def test_fetch_rev_sha(self, mock_call):
        """Verify the commands to fetch from a Git repository w/ SHA."""
        self.shell.git_fetch('mock.git', 'abcdef1234' * 4)
        assert_calls(mock_call, [
            "git remote rm origin",
            "git remote add origin mock.git",
            "git fetch --tags --force --prune origin",
        ])

    def test_fetch_rev_revparse(self, mock_call):
        """Verify the commands to fetch from a Git repository w/ rev-parse."""
        self.shell.git_fetch('mock.git', 'master@{2015-02-12 18:30:00}')
        assert_calls(mock_call, [
            "git remote rm origin",
            "git remote add origin mock.git",
            "git fetch --tags --force --prune origin",
        ])

    def test_changes(self, mock_call):
        """Verify the commands to check for uncommitted changes."""
        self.shell.git_changes()
        assert_calls(mock_call, [
            # based on: http://stackoverflow.com/questions/3878624
            "git update-index -q --refresh",
            "git diff-index --quiet HEAD",
            "git ls-files --others --exclude-standard",
        ])

    def test_changes_false(self, _):
        """Verify the absence of changes can be detected."""
        with patch('gdm.shell.call', Mock(return_value="")):
            assert False is self.shell.git_changes()

    def test_changes_true_untracked(self, _):
        """Verify untracked files can be detected."""
        with patch('gdm.shell.call', Mock(return_value="file_1")):
            assert True is self.shell.git_changes()

    def test_changes_true_uncommitted(self, _):
        """Verify uncommitted changes can be detected."""
        with patch('gdm.shell.call', Mock(side_effect=CallException)):
            assert True is self.shell.git_changes()

    def test_update(self, mock_call):
        """Verify the commands to update a working tree to a revision."""
        self.shell.git_update('mock_rev')
        assert_calls(mock_call, [
            "git stash",
            "git clean --force -d -x",
            "git checkout --force mock_rev",
            "git branch --set-upstream-to origin/mock_rev",
        ])

    def test_update_branch(self, mock_call):
        """Verify the commands to update a working tree to a branch."""
        self.shell.git_update('mock_branch', fetch=True)
        assert_calls(mock_call, [
            "git stash",
            "git clean --force -d -x",
            "git checkout --force mock_branch",
            "git branch --set-upstream-to origin/mock_branch",
            "git pull --ff-only --no-rebase",
        ])

    def test_update_no_clean(self, mock_call):
        self.shell.git_update('mock_rev', clean=False)
        assert_calls(mock_call, [
            "git stash",
            "git checkout --force mock_rev",
            "git branch --set-upstream-to origin/mock_rev",
        ])

    def test_update_revparse(self, mock_call):
        """Verify the commands to update a working tree to a rev-parse."""
        mock_call.return_value = "abc123"
        self.shell.git_update('mock_branch@{2015-02-12 18:30:00}')
        assert_calls(mock_call, [
            "git stash",
            "git clean --force -d -x",
            "git checkout --force mock_branch",
            "git rev-list -n 1 --before='2015-02-12 18:30:00' mock_branch",
            "git checkout --force abc123",
            "git branch --set-upstream-to origin/abc123",
        ])

    def test_get_url(self, mock_call):
        """Verify the commands to get the current repository's URL."""
        self.shell.git_get_url()
        assert_calls(mock_call, ["git config --get remote.origin.url"])

    def test_get_hash(self, mock_call):
        """Verify the commands to get the working tree's hash."""
        self.shell.git_get_hash()
        assert_calls(mock_call, ["git rev-parse HEAD"])

    def test_get_tag(self, mock_call):
        """Verify the commands to get the working tree's tag."""
        self.shell.git_get_tag()
        assert_calls(mock_call, ["git describe --tags --exact-match"])

    def test_get_branch(self, mock_call):
        """Verify the commands to get the working tree's branch."""
        self.shell.git_get_branch()
        assert_calls(mock_call, ["git rev-parse --abbrev-ref HEAD"])
