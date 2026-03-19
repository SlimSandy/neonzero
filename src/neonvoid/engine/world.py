"""World builder - creates and manages the game filesystem."""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path


# Default game directory
DEFAULT_GAME_DIR = Path.home() / ".neonvoid"

# Files that need special permissions (chmod puzzle)
LOCKED_FILES = {
    "local/docs/project_lethe_summary.txt": 0o000,
}

# Directories that should only be created when their server is "connected"
SERVER_DIRS = ["nexus-core", "archive", "lab-9"]

# The escape directory is created dynamically in Act 4
DYNAMIC_DIRS = {
    "lab-9/escape": ["read_own_surveillance", "found_schedule"],
}


def create_game_world(data_dir: Path, game_dir: Path | None = None) -> Path:
    """Create the game filesystem from template data files.

    Args:
        data_dir: Path to the data/filesystem/ directory with template files.
        game_dir: Where to create the game world. Defaults to ~/.neonvoid/

    Returns:
        The path to the created game directory.
    """
    if game_dir is None:
        game_dir = DEFAULT_GAME_DIR

    # Clean slate
    if game_dir.exists():
        # Make everything writable first so we can delete
        _make_writable(game_dir)
        shutil.rmtree(game_dir)

    game_dir.mkdir(parents=True, exist_ok=True)

    # Only copy the "local" server initially - others are created on SSH
    local_src = data_dir / "local"
    local_dst = game_dir / "local"
    if local_src.exists():
        shutil.copytree(local_src, local_dst)

    # Apply special permissions
    for rel_path, mode in LOCKED_FILES.items():
        file_path = game_dir / rel_path
        if file_path.exists():
            os.chmod(file_path, mode)

    # Create save directory
    (game_dir / ".save").mkdir(exist_ok=True)

    return game_dir


def create_server_filesystem(server: str, data_dir: Path, game_dir: Path):
    """Create a server's filesystem when the player SSHs into it.

    Args:
        server: Server name (nexus-core, archive, lab-9).
        data_dir: Path to data/filesystem/.
        game_dir: The game world root.
    """
    server_src = data_dir / server
    server_dst = game_dir / server

    if server_dst.exists():
        return  # Already created

    if server_src.exists():
        shutil.copytree(server_src, server_dst)
    else:
        server_dst.mkdir(parents=True, exist_ok=True)


def create_escape_directory(data_dir: Path, game_dir: Path):
    """Create the escape directory in lab-9 (triggered dynamically in Act 4)."""
    escape_src = data_dir / "lab-9" / "escape"
    escape_dst = game_dir / "lab-9" / "escape"

    if escape_dst.exists():
        return

    if escape_src.exists():
        shutil.copytree(escape_src, escape_dst)
    else:
        # Create minimal escape structure
        escape_dst.mkdir(parents=True, exist_ok=True)
        door_dir = escape_dst / "door_controls"
        door_dir.mkdir(exist_ok=True)
        comms_dir = escape_dst / "comms"
        comms_dir.mkdir(exist_ok=True)


def cleanup_game_world(game_dir: Path | None = None):
    """Remove the game filesystem."""
    if game_dir is None:
        game_dir = DEFAULT_GAME_DIR
    if game_dir.exists():
        _make_writable(game_dir)
        shutil.rmtree(game_dir)


def _make_writable(path: Path):
    """Recursively make all files writable (needed to delete chmod'd files)."""
    for root, dirs, files in os.walk(path):
        for d in dirs:
            dp = Path(root) / d
            try:
                dp.chmod(stat.S_IRWXU)
            except OSError:
                pass
        for f in files:
            fp = Path(root) / f
            try:
                fp.chmod(stat.S_IRWXU)
            except OSError:
                pass
