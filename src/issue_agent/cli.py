from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import sys
import argparse
from datetime import datetime

# Constants
USV_DELIM = '\x1f'
ISSUES_ROOT = Path("docs/issues")
MISSION_PATH = ISSUES_ROOT / "mission.usv"

class Issue(BaseModel):
    slug: str
    priority: int
    status: str
    branch: str

    def to_usv(self) -> str:
        return f"{self.slug}{USV_DELIM}{self.priority}{USV_DELIM}{self.status}{USV_DELIM}{self.branch}"

def load_mission() -> List[Issue]:
    if not MISSION_PATH.exists():
        return []
    
    issues = []
    with MISSION_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(USV_DELIM)
            if len(parts) >= 4:
                try:
                    issues.append(Issue(
                        slug=parts[0],
                        priority=int(parts[1]),
                        status=parts[2],
                        branch=parts[3]
                    ))
                except (ValueError, IndexError):
                    continue
    return issues

def save_mission(issues: List[Issue]):
    """Save the list of issues back to mission.usv."""
    with MISSION_PATH.open("w", encoding="utf-8", newline='\r\n') as f:
        for issue in issues:
            f.write(issue.to_usv() + "\r\n")

def find_issue_file(slug: str) -> Optional[Path]:
    """Find the issue markdown file by slug in docs/issues/ excluding completed/."""
    # We check subdirectories like pending/, draft/, active/
    # but explicitly skip completed/
    search_dirs = [d for d in ISSUES_ROOT.iterdir() if d.is_dir() and d.name != "completed"]
    
    for directory in search_dirs:
        # Check if the file exists in this directory
        issue_file = directory / f"{slug}.md"
        if issue_file.exists():
            return issue_file
            
    return None

def cmd_next(console: Console):
    """Show the top issue."""
    issues = load_mission()
    if not issues:
        console.print("[yellow]No issues found in mission.usv[/yellow]")
        return
        
    next_issue = issues[0]
    issue_file = find_issue_file(next_issue.slug)
    
    if not issue_file:
        console.print(f"[red]Issue file not found for slug: {next_issue.slug}[/red]")
        sys.exit(1)
        
    with issue_file.open("r", encoding="utf-8") as f:
        content = f.read()
        
    console.print(Panel(
        f"[bold blue]NEXT ISSUE:[/bold blue] [cyan]{next_issue.slug}[/cyan]\n"
        f"[bold blue]PRIORITY:[/bold blue] {next_issue.priority} | "
        f"[bold blue]STATUS:[/bold blue] {next_issue.status} | "
        f"[bold blue]BRANCH:[/bold blue] {next_issue.branch}\n"
        f"[bold blue]FILE:[/bold blue] {issue_file}",
        title="Issue Agent",
        expand=False
    ))
    
    md = Markdown(content)
    console.print(md)

def cmd_done(console: Console, slug: Optional[str] = None):
    """Mark an issue as done."""
    issues = load_mission()
    if not issues:
        console.print("[yellow]No issues found in mission.usv[/yellow]")
        return

    # If no slug provided, use the top one
    if slug is None:
        target_issue = issues[0]
    else:
        # Find the issue with the given slug
        target_issue = next((i for i in issues if i.slug == slug), None)
        if not target_issue:
            console.print(f"[red]Issue with slug '{slug}' not found in mission.usv[/red]")
            sys.exit(1)

    issue_file = find_issue_file(target_issue.slug)
    if not issue_file:
        console.print(f"[red]Issue file not found for slug: {target_issue.slug}[/red]")
        # We might still want to remove it from mission.usv if requested?
        # For now, let's just exit.
        sys.exit(1)

    # Move to completed/{year}/
    year = datetime.now().year
    completed_dir = ISSUES_ROOT / "completed" / str(year)
    completed_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path = completed_dir / f"{target_issue.slug}.md"
    
    console.print(f"[green]Moving {issue_file} to {dest_path}...[/green]")
    issue_file.rename(dest_path)

    # Remove from mission.usv
    new_issues = [i for i in issues if i.slug != target_issue.slug]
    save_mission(new_issues)
    console.print(f"[bold green]Issue '{target_issue.slug}' marked as done and removed from mission.usv[/bold green]")

def main():
    parser = argparse.ArgumentParser(description="Issue Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    # next
    subparsers.add_parser("next", help="Show the top issue")
    
    # done
    done_parser = subparsers.add_parser("done", help="Mark an issue as done")
    done_parser.add_argument("slug", nargs="?", help="Slug of the issue to mark as done (defaults to top issue)")

    args = parser.parse_args()
    console = Console()

    if args.command == "next":
        cmd_next(console)
    elif args.command == "done":
        cmd_done(console, args.slug)
    else:
        # Default to 'next' if no command given? Or show help.
        if len(sys.argv) == 1:
            cmd_next(console)
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
