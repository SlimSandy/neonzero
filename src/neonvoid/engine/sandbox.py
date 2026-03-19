"""Filesystem sandbox - ensures all operations stay within the game directory."""

from pathlib import Path


class Sandbox:
    """Constrains all file operations to a game root directory."""

    def __init__(self, game_root: Path):
        self.game_root = game_root.resolve()

    def resolve(self, path: str, cwd: Path) -> Path:
        """Resolve a path string relative to cwd, constrained to game_root.

        Args:
            path: The path string from user input (may be relative or absolute).
            cwd: The current working directory (must be within game_root).

        Returns:
            Resolved absolute Path within the sandbox.

        Raises:
            PermissionError: If the resolved path escapes the sandbox.
        """
        if path.startswith("/"):
            # Treat absolute paths as relative to game root
            candidate = (self.game_root / path.lstrip("/")).resolve()
        elif path.startswith("~"):
            candidate = (self.game_root / path.lstrip("~/")).resolve()
        else:
            candidate = (cwd / path).resolve()

        if not self._is_within(candidate):
            raise PermissionError("Access denied: path outside permitted area")

        return candidate

    def resolve_or_none(self, path: str, cwd: Path) -> Path | None:
        """Like resolve, but returns None instead of raising."""
        try:
            return self.resolve(path, cwd)
        except PermissionError:
            return None

    def _is_within(self, path: Path) -> bool:
        """Check if a path is within (or equal to) the game root."""
        try:
            path.relative_to(self.game_root)
            return True
        except ValueError:
            return False

    def relative_display(self, path: Path) -> str:
        """Get a display-friendly path relative to game root, shown as ~/..."""
        try:
            rel = path.relative_to(self.game_root)
            return f"~/{rel}" if str(rel) != "." else "~"
        except ValueError:
            return str(path)

    def is_within(self, path: Path) -> bool:
        """Public check if a path is within the sandbox."""
        return self._is_within(path.resolve())
