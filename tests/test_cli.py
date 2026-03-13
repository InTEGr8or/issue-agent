import pytest
from taskagent.cli import (
    cmd_new,
    cmd_done,
    cmd_ingest,
    cmd_promote,
)
from taskagent.manager import TaskAgent
from rich.console import Console
from datetime import datetime


@pytest.fixture
def temp_issues_dir(tmp_path):
    """Create a temporary issues structure."""
    issues_root = tmp_path / "docs" / "issues"
    for subdir in ["pending", "draft", "active", "completed"]:
        (issues_root / subdir).mkdir(parents=True)
    return issues_root


@pytest.fixture
def manager(temp_issues_dir):
    return TaskAgent(config_dir=str(temp_issues_dir))


def test_slugify(manager):
    assert manager.slugify("Hello World") == "hello-world"
    assert manager.slugify("Task: Do Something!") == "task-do-something"
    assert manager.slugify("Already-Slugified") == "already-slugified"


def test_cmd_new_file(manager, temp_issues_dir):
    console = Console()
    cmd_new(console, manager, "Test Task", "Task Body", draft=False)

    issue_file = temp_issues_dir / "pending" / "test-task.md"
    assert issue_file.exists()
    assert "# Test Task" in issue_file.read_text()

    issues = manager.load_mission()
    assert len(issues) == 1
    assert issues[0].slug == "test-task"
    assert issues[0].status == "pending"


def test_cmd_new_dir(manager, temp_issues_dir):
    console = Console()
    cmd_new(
        console,
        manager,
        "Dir Task",
        "Body",
        draft=True,
        as_dir=True,
    )

    readme = temp_issues_dir / "draft" / "dir-task" / "README.md"
    assert readme.exists()

    issues = manager.load_mission()
    assert issues[0].slug == "dir-task"
    assert issues[0].status == "draft"


def test_cmd_done(manager, temp_issues_dir):
    console = Console()
    cmd_new(console, manager, "Done Task", "Body", draft=False)

    cmd_done(console, manager, "done-task", should_commit=False)

    # Should be in completed/year/
    year = str(datetime.now().year)
    completed_file = temp_issues_dir / "completed" / year / "done-task.md"
    assert completed_file.exists()
    assert "Completed in commit" in completed_file.read_text()

    # Should be removed from mission
    issues = manager.load_mission()
    assert len(issues) == 0


def test_cmd_ingest(manager, temp_issues_dir):
    console = Console()
    # Create files manually
    (temp_issues_dir / "pending" / "task-1.md").write_text("# Task 1")
    (temp_issues_dir / "draft" / "task-2").mkdir()
    (temp_issues_dir / "draft" / "task-2" / "README.md").write_text(
        "# Task 2\n\n**Depends on:** task-1"
    )

    cmd_ingest(console, manager)

    issues = manager.load_mission()
    assert len(issues) == 2
    assert issues[0].slug == "task-1"
    assert issues[1].slug == "task-2"
    assert issues[1].dependencies == ["task-1"]

    assert (temp_issues_dir / "datapackage.json").exists()


def test_cmd_start(manager, temp_issues_dir, monkeypatch):
    from taskagent import cli
    import subprocess

    console = Console()
    cmd_new(console, manager, "Start Task", "Body", draft=False)

    calls = []

    def mock_run(args, **kwargs):
        calls.append(args)

        class MockCompletedProcess:
            returncode = 0
            stdout = ""
            stderr = ""

        return MockCompletedProcess()

    monkeypatch.setattr(subprocess, "run", mock_run)

    cli.cmd_start(console, manager, "start-task")

    assert (temp_issues_dir / "active" / "start-task.md").exists()
    assert not (temp_issues_dir / "pending" / "start-task.md").exists()
    assert len(calls) > 0


def test_cmd_run(manager, temp_issues_dir, monkeypatch):
    from taskagent import cli
    import subprocess
    from pathlib import Path

    console = Console()

    # Create an active issue
    cmd_new(console, manager, "Run Task", "Body", draft=False)
    cli.cmd_active(console, manager, "run-task", silent=True)

    calls = []

    def mock_run(args, **kwargs):
        calls.append((args, kwargs.get("env", {})))

        class MockCompletedProcess:
            returncode = 0

        return MockCompletedProcess()

    monkeypatch.setattr(subprocess, "run", mock_run)

    original_exists = Path.exists

    def mock_exists(self):
        if str(self).endswith(".ta/worker"):
            return True
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", mock_exists)
    monkeypatch.setattr("os.access", lambda path, mode: True)

    cli.cmd_run(console, manager, "run-task")

    assert len(calls) == 1
    args, env = calls[0]
    assert str(args[0]).endswith(".ta/worker")
    assert env["TA_SLUG"] == "run-task"


def test_cmd_promote(manager, temp_issues_dir):
    console = Console()
    cmd_new(console, manager, "Draft Task", "Body", draft=True)

    cmd_promote(console, manager, "draft-t")

    assert (temp_issues_dir / "pending" / "draft-task.md").exists()
    assert not (temp_issues_dir / "draft" / "draft-task.md").exists()

    issues = manager.load_mission()
    assert issues[0].status == "pending"
