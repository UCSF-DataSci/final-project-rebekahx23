"""Data quality multi-agent package."""

try:
    from .agent import app, root_agent
except ModuleNotFoundError:  # pragma: no cover - allows local lab utilities without ADK installed
    app = None
    root_agent = None

__all__ = ["app", "root_agent"]
