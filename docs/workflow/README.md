# Workflow 🚀

Task Agent is designed to support a lean, git-centric development workflow. Here is the recommended way to use it.

## 1. Capturing Ideas (Drafts)
When you have an idea but aren't ready to commit to it, create it as a **draft**:
```bash
ta new "Refactor database layer" --draft
```
This puts the task in `docs/issues/draft/` where it won't clutter your active backlog.

## 2. Planning (Pending)
When a task is ready to be worked on, **promote** it:
```bash
ta promote refactor-db
```
The task is now in the `pending/` backlog. You can use `ta up` and `ta down` to move it within the prioritized queue.

## 3. Execution (Active)
When you (or an agent) start working on a task, mark it as **active**:
```bash
ta active refactor-db
```
This signals to others that the task is currently being handled.

## 4. Finalizing (Done)
Once the work is verified, complete the task:
```bash
ta done refactor-db -m "refactor: improve db connection pooling"
```
This command is the "closing loop" of the workflow:
- It commits your work.
- It moves the task to the annual archive.
- It records the exact commit hash in the task documentation for future reference.
- It bumps your project's version automatically.

## 🤝 Human-Agent Collaboration
Task Agent is an ideal "Mission Control" for AI agents.
1.  **Humans** create and prioritize tasks in `pending`.
2.  **Agents** pick the top task using `ta next`.
3.  **Agents** mark it `active` and perform the work.
4.  **Agents** (or humans after review) mark it `done`.
