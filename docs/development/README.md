# Development ⚙️

This document covers how to set up the development environment, run tests, and release new versions of Task Agent.

## 🛠️ Environment Setup

Task Agent uses **`uv`** for dependency management and **`mise`** for toolchain control.

1.  Install `uv` and `mise`.
2.  Install dependencies and set up the virtual environment:
    ```bash
    uv sync
    ```
3.  Activate the environment:
    ```bash
    mise install
    ```

## 🧪 Testing

We use **`pytest`** for automated testing.

To run the test suite:
```bash
make test
```

## 🧹 Linting

We use **`ruff`** for linting and formatting, and **`mypy`** for type checking.

To run all checks:
```bash
make lint
```

## 📦 Releasing

Releases are automated via GitHub Actions when a tag is pushed.

1.  Bump the version:
    ```bash
    ta version promote patch  # or minor/major
    ```
2.  Tag and push:
    ```bash
    ta version tag
    git push origin master --tags
    ```

## 🤖 Continuous Integration

Every push to `master` triggers the following:
- `ruff` checks and formatting validation.
- `mypy` type checking.
- Automated tests via `pytest`.
