from typing import Optional
from mcp.server.fastmcp import FastMCP

from taskagent.manager import TaskAgent
from taskagent.discovery import discover

# Create an MCP server
mcp = FastMCP("TaskAgent")


def get_manager() -> TaskAgent:
    """Helper to initialize the manager based on current environment."""
    return discover()


@mcp.tool()
def list_tasks() -> str:
    """List all tasks in the current project's mission queue."""
    manager = get_manager()
    issues = manager.sync_mission()
    if not issues:
        return "No tasks found in the queue."

    lines = []
    for i in issues:
        deps = f" (depends on: {', '.join(i.dependencies)})" if i.dependencies else ""
        lines.append(f"[{i.priority}] {i.status.upper()}: {i.slug}{deps}")
    return "\n".join(lines)


@mcp.tool()
def create_task(
    title: str, body: str = "", draft: bool = False, depends_on: Optional[str] = None
) -> str:
    """Create a new task in the mission queue.

    Args:
        title: The title of the task.
        body: Detailed description of the task.
        draft: If True, creates the task in 'draft' status. Default is False (pending).
        depends_on: Comma-separated list of existing task slugs this task depends on.
    """
    manager = get_manager()
    try:
        issue = manager.create_issue(title, body, draft, depends_on)
        return f"Created task: {issue.slug} (Status: {issue.status})"
    except Exception as e:
        return f"Error creating task: {e}"


@mcp.tool()
def promote_task(slug: str) -> str:
    """Promote a task from 'draft' to 'pending' status."""
    manager = get_manager()
    try:
        manager.promote_issue(slug)
        return f"Task '{slug}' promoted to pending."
    except Exception as e:
        return f"Error promoting task: {e}"


@mcp.tool()
def demote_task(slug: str) -> str:
    """Demote a task from 'pending' back to 'draft' status."""
    manager = get_manager()
    try:
        manager.demote_issue(slug)
        return f"Task '{slug}' demoted to draft."
    except Exception as e:
        return f"Error demoting task: {e}"


@mcp.tool()
def mark_task_active(slug: str) -> str:
    """Move a task to 'active' status, indicating work has started."""
    manager = get_manager()
    try:
        manager.move_to_active(slug)
        return f"Task '{slug}' is now active."
    except Exception as e:
        return f"Error marking task active: {e}"


@mcp.tool()
def complete_task(slug: str, message: Optional[str] = None) -> str:
    """Mark a task as completed and commit the changes.

    Args:
        slug: The slug of the task to complete.
        message: Optional git commit message.
    """
    manager = get_manager()
    try:
        issue, commit_hash = manager.complete_issue(slug, commit_message=message)
        return f"Task '{slug}' completed. Commit: {commit_hash}"
    except Exception as e:
        return f"Error completing task: {e}"


@mcp.tool()
def search_task(slug: str) -> str:
    """Search for a task by slug, including in completed tasks.

    Args:
        slug: The slug of the task to search for.
    """
    manager = get_manager()
    issue_file = manager.find_issue_file(slug, include_completed=True)
    if not issue_file:
        return f"Task '{slug}' not found anywhere."

    # Determine status based on path
    status = "unknown"
    for s in ["pending", "draft", "active", "completed"]:
        if f"/{s}/" in str(issue_file.absolute()):
            status = s
            break

    return f"Task '{slug}' found in [bold]{status}[/bold]. Location: {issue_file}"


@mcp.tool()
def restore_task(slug: str, status: str = "pending") -> str:
    """Restore a completed task back to pending, draft, or active status.

    Args:
        slug: The slug of the task to restore.
        status: The target status ('pending', 'draft', or 'active'). Defaults to 'pending'.
    """
    manager = get_manager()
    try:
        manager.restore_issue(slug, to_status=status)
        return f"Task '{slug}' restored to '{status}'."
    except Exception as e:
        return f"Error restoring task: {e}"


@mcp.tool()
def get_task_details(slug: str) -> str:
    """Get the full description and content of a specific task."""
    manager = get_manager()
    issue_file = manager.find_issue_file(slug)
    if not issue_file:
        return f"Task '{slug}' not found."

    return issue_file.read_text(encoding="utf-8")


def run_mcp_server():
    """Main entry point to run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    run_mcp_server()
