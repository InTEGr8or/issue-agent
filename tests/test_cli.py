import pytest
from taskagent.cli import slugify, load_mission, cmd_new, cmd_done, cmd_ingest
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
