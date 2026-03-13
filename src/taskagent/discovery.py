import os
import json
from pathlib import Path
from typing import Optional
from taskagent.manager import TaskAgent


def discover(start_path: Optional[Path] = None) -> TaskAgent:
    """
    Standard discovery mechanism for task-agent.

    Checks in order:
    1. TA_CONFIG_DIR environment variable.
    2. .ta-config.json in start_path or any parent.
    3. pyproject.toml [tool.taskagent] in start_path or any parent.
    4. docs/issues/ directory in start_path or any parent.
    5. ~/.config/task-agent/settings.json (Global fallback)

    Returns:
        TaskAgent: Initialized manager for the discovered instance.
    """
    if os.environ.get("TA_CONFIG_DIR"):
        return TaskAgent()

    current = Path(start_path or Path.cwd()).absolute()

    while True:
        # 1. Check for explicit config file
        config_file = current / ".ta-config.json"
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                if "issues_dir" in config:
                    return TaskAgent(config_dir=str(current / config["issues_dir"]))
            except Exception:
                pass

        # 2. Check for pyproject.toml
        pyproject = current / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomllib

                with pyproject.open("rb") as f:
                    data = tomllib.load(f)
                    ta_cfg = data.get("tool", {}).get("taskagent")
                    if ta_cfg and "issues_dir" in ta_cfg:
                        return TaskAgent(config_dir=str(current / ta_cfg["issues_dir"]))
            except Exception:
                # Fallback if tomllib is missing or parse fails
                pass

        # 3. Check for standard folder
        issues_dir = current / "docs" / "issues"
        if issues_dir.exists() and issues_dir.is_dir():
            return TaskAgent(config_dir=str(issues_dir))

        # Move up
        parent = current.parent
        if parent == current:
            break
        current = parent

    # 4. Check Global Config
    global_config = Path("~/.config/task-agent/settings.json").expanduser()
    if global_config.exists():
        try:
            config = json.loads(global_config.read_text())
            if "issues_dir" in config:
                return TaskAgent(config_dir=config["issues_dir"])
        except Exception:
            pass

    # Fallback to default (which will create docs/issues in starting search dir if not found)
    # We use start_path or cwd as the base
    fallback_base = Path(start_path or Path.cwd()).absolute()
    return TaskAgent(config_dir=str(fallback_base / "docs" / "issues"))
