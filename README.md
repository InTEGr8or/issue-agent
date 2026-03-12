# Task Agent 🤖

A prioritized, file-based task queue for autonomous agentic workers. This system uses a "Mission Control" approach to manage multiple agents working on git-tracked improvements across various branches and worktrees.

## 📂 System Architecture

The project follows a specific folder structure to manage the lifecycle of an improvement:

- `docs/issues/`: The core queue.
    - `mission.usv`: A prioritized list of issues using Unit Separator Value (`\x1f`) format. This serves as the source of truth for task priority.
    - `datapackage.json`: Frictionless Data metadata for the `mission.usv` schema.
    - `pending/`: New issues awaiting triage or assignment.
    - `draft/`: Issues currently being refined or planned.
    - `active/`: Issues actively being worked on by an agent.
    - `completed/{year}/`: Successfully implemented and verified improvements.
- `.gwt/`: Git Worktree directory where active branches are checked out for isolated agent execution.

## 🛠️ Tooling: `ta` (Task Agent CLI)

The `ta` tool automates the transition of issues through the queue and manages the underlying git infrastructure.

### Commands

| Command | Action |
| :--- | :--- |
| `ta next` | Displays the top prioritized issue from `mission.usv`. |
| `ta new` | Creates a new issue file and adds it to the queue. |
| `ta done` | Moves issue to `completed/`, removes it from the queue, and auto-commits the result. |
| `ta start <slug>` | Moves issue to `active/`, creates a git branch, and sets up a `.gwt/` worktree. |
| `ta run <slug>` | Invokes the sidecar worker defined at `.ta/worker` to process an active issue. |

## 🚀 Workflow

1. **Prioritize**: Use `ta new -t "Title"` to add a task.
2. **Review**: Run `ta next` to see what is currently at the top of the queue.
3. **Dispatch**: (Planned) Run `ta start <slug>` to prepare the workspace.
4. **Execute**: (Planned) The agent (Gemini CLI) processes the task in its isolated worktree via `ta run <slug>`.
5. **Finalize**: Once verified, `ta done` moves the task to the finished state.

## 🤖 Gemini CLI Integration

By utilizing the Gemini CLI's headless mode, this system can orchestrate multiple agents simultaneously without requiring manual terminal management, significantly improving portability and scalability between Windows and WSL environments.
