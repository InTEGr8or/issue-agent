# Project Mandates

## Data Integrity
- **Task Management**: NEVER modify `mission.usv` or `datapackage.json` directly. These files are managed by the Task Agent (`ta`) tool. Direct edits often corrupt the format (USV Unit Separators) or break prioritization. Always use the `ta` CLI or the `task-agent` MCP tools to manage tasks.
- **Workflow Compliance**: Use `ta next` to discover work and `ta active` to signal assignment before starting a task.
