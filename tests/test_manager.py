import pytest
from taskagent.manager import TaskAgent
from datetime import datetime


@pytest.fixture
def manager(tmp_path):
    issues_root = tmp_path / "docs" / "issues"
    return TaskAgent(config_dir=str(issues_root))


def test_api_create_issue(manager):
    issue = manager.create_issue("API Task", body="Body from API")
    assert issue.slug == "api-task"
    assert issue.status == "pending"

    # Check filesystem
    file = manager.issues_root / "pending" / "api-task.md"
    assert file.exists()
    assert "Body from API" in file.read_text()


def test_api_complete_issue(manager):
    manager.create_issue("Complete Me")
    # complete_issue returns (issue, commit_hash)
    issue, commit = manager.complete_issue("complete-me", should_commit=False)

    assert issue.slug == "complete-me"
    assert issue.status == "completed"

    year = str(datetime.now().year)
    assert (manager.issues_root / "completed" / year / "complete-me.md").exists()


def test_api_sync_mission(manager):
    manager.create_issue("Task A", draft=True)
    manager.create_issue("Task B", draft=False)

    issues = manager.sync_mission()
    # pending (B) should be before draft (A)
    assert issues[0].slug == "task-b"
    assert issues[1].slug == "task-a"


def test_api_demote_issue(manager):
    manager.create_issue("Demote Me")
    # Starts as pending
    assert (manager.issues_root / "pending" / "demote-me.md").exists()

    manager.demote_issue("demote-me")
    assert not (manager.issues_root / "pending" / "demote-me.md").exists()
    assert (manager.issues_root / "draft" / "demote-me.md").exists()
