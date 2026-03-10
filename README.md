# Issue Agent 🤖

A prioritized, file-based task queue for autonomous agentic workers. This system uses a "Mission Control" approach to manage multiple agents working on git-tracked improvements across various branches and worktrees.

## 📂 System Architecture

The project follows a specific folder structure to manage the lifecycle of an improvement:

- `docs/issues/`: The core queue.
    - `pending/`: New issues awaiting triage or assignment.
    - `draft/`: Issues currently being refined or planned.
    - `active/`: Issues actively being worked on by an agent.
    - `completed/`: Successfully implemented and verified improvements.
- `mission.usv`: A prioritized list of issues using Unit Separator Value (`\x1f`) format. This serves as the source of truth for task priority.
- `datapackage.json`: Frictionless Data metadata for the `mission.usv` schema.
- `.gwt/`: Git Worktree directory where active branches are checked out for isolated agent execution.

## 🛠️ Tooling: `ia` (Issue Agent CLI)

The `ia` tool (to be implemented) automates the transition of issues through the queue and manages the underlying git infrastructure.

### Planned Commands

| Command | Action |
| :--- | :--- |
| `ia list` | Displays the prioritized queue from `mission.usv`. |
| `ia start <slug>` | Moves issue to `active/`, creates a git branch, and sets up a `.gwt/` worktree. |
| `ia run <slug>` | Invokes Gemini CLI in **headless mode** within the issue's specific worktree. |
| `ia complete <slug>` | Moves issue to `completed/`, cleans up the worktree, and updates status. |

## 🚀 Workflow

1. **Prioritize**: Add a slug to `mission.usv` and place the task description in `docs/issues/pending/<slug>.md`.
2. **Dispatch**: Run `ia start <slug>` to prepare the workspace.
3. **Execute**: The agent (Gemini CLI) processes the task in its isolated worktree via `ia run <slug>`.
4. **Finalize**: Once verified, `ia complete <slug>` moves the task to the finished state and merges/cleans up.

## 🤖 Gemini CLI Integration

By utilizing the Gemini CLI's headless mode, this system can orchestrate multiple agents simultaneously without requiring manual terminal management, significantly improving portability and scalability between Windows and WSL environments.
