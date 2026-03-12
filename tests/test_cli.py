import pytest
from taskagent.cli import (
    slugify,
    load_mission,
    cmd_new,
    cmd_done,
    cmd_ingest,
    cmd_promote,
)
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
def mission_path(temp_issues_dir):
    return temp_issues_dir / "mission.usv"


def test_slugify():
    assert slugify("Hello World") == "hello-world"
    assert slugify("Task: Do Something!") == "task-do-something"
    assert slugify("Already-Slugified") == "already-slugified"


def test_cmd_new_file(temp_issues_dir, mission_path):
    console = Console()
    cmd_new(
        console, temp_issues_dir, mission_path, "Test Task", "Task Body", draft=False
    )

    issue_file = temp_issues_dir / "pending" / "test-task.md"
    assert issue_file.exists()
    assert "# Test Task" in issue_file.read_text()

    issues = load_mission(temp_issues_dir, mission_path)
    assert len(issues) == 1
    assert issues[0].slug == "test-task"
    assert issues[0].status == "pending"


def test_cmd_new_dir(temp_issues_dir, mission_path):
    console = Console()
    cmd_new(
        console,
        temp_issues_dir,
        mission_path,
        "Dir Task",
        "Body",
        draft=True,
        as_dir=True,
    )

    readme = temp_issues_dir / "draft" / "dir-task" / "README.md"
    assert readme.exists()

    issues = load_mission(temp_issues_dir, mission_path)
    assert issues[0].slug == "dir-task"
    assert issues[0].status == "draft"


def test_cmd_new_depends_on(temp_issues_dir, mission_path):
    console = Console()
    cmd_new(
        console, temp_issues_dir, mission_path, "B", "Body", draft=False, depends_on="A"
    )

    issues = load_mission(temp_issues_dir, mission_path)
    assert issues[0].dependencies == ["A"]
    assert "**Depends on:** A" in (temp_issues_dir / "pending" / "b.md").read_text()


def test_cmd_done(temp_issues_dir, mission_path):
    console = Console()
    cmd_new(console, temp_issues_dir, mission_path, "Done Task", "Body", draft=False)

    cmd_done(console, temp_issues_dir, mission_path, "done-task")

    # Should be in completed/year/
    year = str(datetime.now().year)
    completed_file = temp_issues_dir / "completed" / year / "done-task.md"
    assert completed_file.exists()
    assert "Completed in commit" in completed_file.read_text()

    # Should be removed from mission
    issues = load_mission(temp_issues_dir, mission_path)
    assert len(issues) == 0


def test_cmd_ingest(temp_issues_dir, mission_path):
    console = Console()
    # Create files manually
    (temp_issues_dir / "pending" / "task-1.md").write_text("# Task 1")
    (temp_issues_dir / "draft" / "task-2").mkdir()
    (temp_issues_dir / "draft" / "task-2" / "README.md").write_text(
        "# Task 2\n\n**Depends on:** task-1"
    )

    cmd_ingest(console, temp_issues_dir, mission_path)

    issues = load_mission(temp_issues_dir, mission_path)
    assert len(issues) == 2
    assert issues[0].slug == "task-1"
    assert issues[1].slug == "task-2"
    assert issues[1].dependencies == ["task-1"]

    assert (temp_issues_dir / "datapackage.json").exists()


def test_cmd_start(temp_issues_dir, mission_path, monkeypatch):
    from taskagent import cli
    import subprocess

    console = Console()
    cmd_new(console, temp_issues_dir, mission_path, "Start Task", "Body", draft=False)

    calls = []

    def mock_run(args, **kwargs):
        calls.append(args)

        # Return a mock object with returncode=0
        class MockCompletedProcess:
            returncode = 0
            stdout = ""
            stderr = ""

        return MockCompletedProcess()

    monkeypatch.setattr(subprocess, "run", mock_run)

    cli.cmd_start(console, temp_issues_dir, mission_path, "start-task")

    # Should be moved to active/
    assert (temp_issues_dir / "active" / "start-task.md").exists()
    assert not (temp_issues_dir / "pending" / "start-task.md").exists()

    # Should have attempted to create worktree
    assert len(calls) > 0
    # Check if any call looks like git worktree add
    wt_call = next((c for c in calls if "worktree" in c and "add" in c), None)
    assert wt_call is not None
    assert "-b" in wt_call
    assert "issue/start-task" in wt_call


def test_cmd_run(temp_issues_dir, mission_path, monkeypatch):
    from taskagent import cli
    import subprocess
    from pathlib import Path

    console = Console()

    # Create an active issue
    cmd_new(console, temp_issues_dir, mission_path, "Run Task", "Body", draft=False)
    cli.cmd_active(console, temp_issues_dir, mission_path, "run-task", silent=True)

    calls = []

    def mock_run(args, **kwargs):
        calls.append((args, kwargs.get("env", {})))

        class MockCompletedProcess:
            returncode = 0

        return MockCompletedProcess()

    monkeypatch.setattr(subprocess, "run", mock_run)

    # Mock existence and executability of .ta/worker
    original_exists = Path.exists

    def mock_exists(self):
        if str(self).endswith(".ta/worker"):
            return True
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", mock_exists)

    monkeypatch.setattr("os.access", lambda path, mode: True)

    cli.cmd_run(console, temp_issues_dir, mission_path, "run-task")

    assert len(calls) == 1
    args, env = calls[0]
    assert str(args[0]).endswith(".ta/worker")
    assert env["TA_SLUG"] == "run-task"
    assert "TA_FILE" in env
    assert "TA_ROOT" in env


def test_cmd_promote(temp_issues_dir, mission_path):
    console = Console()
    cmd_new(console, temp_issues_dir, mission_path, "Draft Task", "Body", draft=True)

    # Promote using partial slug
    cmd_promote(console, temp_issues_dir, mission_path, "draft-t")

    assert (temp_issues_dir / "pending" / "draft-task.md").exists()
    assert not (temp_issues_dir / "draft" / "draft-task.md").exists()

    issues = load_mission(temp_issues_dir, mission_path)
    assert issues[0].status == "pending"
