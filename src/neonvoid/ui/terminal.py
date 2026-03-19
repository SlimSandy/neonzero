"""Rich console wrapper for terminal output."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

NEON_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "bold green",
    "dim": "dim white",
    "server.local": "green",
    "server.nexus-core": "cyan",
    "server.archive": "yellow",
    "server.lab-9": "red",
    "narrative": "italic white",
    "system": "bold cyan",
    "error": "bold red",
    "highlight": "bold magenta",
})

console = Console(theme=NEON_THEME, highlight=False)


def print_output(text: str):
    """Print command output with Rich markup support."""
    if not text:
        return
    console.print(text)


def print_narrative(text: str):
    """Print narrative/story text with special styling."""
    console.print()
    console.print(Panel(
        text,
        border_style="dim cyan",
        padding=(1, 2),
    ))
    console.print()


def print_system(text: str):
    """Print system messages."""
    console.print(f"[system]> {text}[/system]")


def print_error(text: str):
    """Print error messages."""
    console.print(f"[error]{text}[/error]")


def print_warning(text: str):
    """Print warning messages."""
    console.print(f"[warning]{text}[/warning]")


def print_divider():
    """Print a styled divider line."""
    console.print("[dim]" + "─" * 60 + "[/dim]")
