# CLI Reference 💻

The `ta` command-line interface provides everything you need to manage your task queue.

## 📋 General Options

- `-V`, `--version`: Show the `task-agent` tool version and check for updates.
- `-C`, `--config-dir`: Override the default issues directory (defaults to `docs/issues` or `TA_CONFIG_DIR`).

## 🛠️ Commands

### `ta next`
Displays the highest priority task currently in the queue.
- Uses a pager for long descriptions.
- Automatically sorts the queue before fetching.

### `ta list`
Lists all issues in the mission control file.
- **Flags**:
  - `--json`: Machine-readable output.
  - `--text`: Simple, borderless text output for small screens.
- **Sorting**: Groups tasks by `active`, `pending`, and `draft`.
- **Nesting**: Displays dependent tasks indented under their parents.

### `ta new <title>`
Creates a new task.
- **Flags**:
  - `-b`, `--body`: The task description.
  - `-d`, `--draft`: Create the task in the `draft/` directory.
  - `--dir`: Create a directory-based task (`slug/README.md`).
  - `--depends-on <slugs>`: Comma-separated list of dependencies.

### `ta active [slug]`
Marks a task as active.
- Moves the task to the `active/` directory.
- Supports partial slug matching.

### `ta done [slug]`
Marks a task as completed.
- **Flags**:
  - `-m`, `--message`: Custom git commit message.
  - `--no-commit`: Skip the automatic git commit.
- **Process**:
  1. Moves the file to `completed/{year}/`.
  2. Commits changes to the repository.
  3. Appends the resulting commit hash to the task file.
  4. Increments the project patch version (if `pyproject.toml` or `package.json` is present).

### `ta promote <slug>`
Moves a task from `draft/` to `pending/`.
- Supports partial slug matching.

### `ta up <slug>` / `ta down <slug>`
Increases or decreases the priority of a task within its status group.
- Supports partial slug matching.

### `ta ingest`
Rebuilds the `mission.usv` and `datapackage.json` based on files found on disk.
- Preserves existing order for known tasks.
- Appends new tasks found in `pending`, `draft`, or `active`.
- Removes entries for missing files.

### `ta version`
Displays and manages the target project's version.
- **Subcommands**:
  - `promote [major|minor|patch]`: Bumps the project version and syncs lockfiles.
  - `tag`: Tags the current commit with the project version.

### `ta self-up`
Upgrades the `task-agent` tool itself via `uv`.
