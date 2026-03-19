"""Base command class and command registry."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from neonvoid.engine.sandbox import Sandbox
    from neonvoid.game.state import GameState


class CommandContext:
    """Context passed to every command execution."""

    def __init__(
        self,
        cwd: Path,
        game_root: Path,
        sandbox: Sandbox,
        state: GameState,
        pipe_input: str | None = None,
    ):
        self.cwd = cwd
        self.game_root = game_root
        self.sandbox = sandbox
        self.state = state
        self.pipe_input = pipe_input
        # Commands can set this to change the cwd
        self.new_cwd: Path | None = None
        # Commands can set this to trigger special actions
        self.action: str | None = None
        self.action_data: dict | None = None


class Command(Protocol):
    """Protocol for command implementations."""

    name: str
    aliases: list[str]
    help_text: str

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        """Execute the command and return output text."""
        ...


class CommandRegistry:
    """Registry of all available commands."""

    def __init__(self):
        self._commands: dict[str, Command] = {}

    def register(self, command: Command):
        """Register a command by its name and aliases."""
        self._commands[command.name] = command
        for alias in command.aliases:
            self._commands[alias] = command

    def get(self, name: str) -> Command | None:
        """Look up a command by name or alias."""
        return self._commands.get(name)

    def all_commands(self) -> list[Command]:
        """Get all unique registered commands."""
        seen = set()
        result = []
        for cmd in self._commands.values():
            if id(cmd) not in seen:
                seen.add(id(cmd))
                result.append(cmd)
        return sorted(result, key=lambda c: c.name)
