"""NEON VOID - Main entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from neonvoid.engine.shell import GameShell
from neonvoid.engine.world import DEFAULT_GAME_DIR, cleanup_game_world, create_game_world
from neonvoid.game.state import GameState
from neonvoid.ui.ascii import TITLE_ART
from neonvoid.ui.effects import boot_sequence
from neonvoid.ui.terminal import console


def get_data_dir() -> Path:
    """Find the data directory relative to this package."""
    # Try relative to this file
    pkg_dir = Path(__file__).parent.parent.parent  # src/neonvoid/main.py -> project root-ish
    candidates = [
        pkg_dir / "data" / "filesystem",
        pkg_dir.parent / "data" / "filesystem",
        Path(__file__).parent.parent / "data" / "filesystem",  # src/data/filesystem
    ]

    # Also check if running from project root
    cwd_candidate = Path.cwd() / "data" / "filesystem"
    candidates.insert(0, cwd_candidate)

    # Check installed package data
    try:
        import importlib.resources as resources
        # For installed package
        pkg_data = Path(__file__).parent.parent / "data" / "filesystem"
        candidates.insert(0, pkg_data)
    except ImportError:
        pass

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    # Last resort: look for data relative to the neonvoid package
    neonvoid_dir = Path(__file__).parent
    data_path = neonvoid_dir / ".." / ".." / "data" / "filesystem"
    if data_path.resolve().exists():
        return data_path.resolve()

    console.print("[bold red]Error: Could not find game data directory.[/bold red]")
    console.print("[dim]Expected 'data/filesystem/' in the project root.[/dim]")
    sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="NEON VOID - A Cyberpunk Terminal RPG")
    parser.add_argument("--new", action="store_true", help="Start a new game (erases save)")
    parser.add_argument("--skip-intro", action="store_true", help="Skip the boot sequence")
    parser.add_argument(
        "--game-dir",
        type=Path,
        default=None,
        help=f"Game directory (default: {DEFAULT_GAME_DIR})",
    )
    args = parser.parse_args()

    game_dir = args.game_dir or DEFAULT_GAME_DIR
    data_dir = get_data_dir()

    # Check for existing save
    save_path = game_dir / ".save" / "state.json"
    state: GameState | None = None

    if not args.new and save_path.exists():
        state = GameState.load(save_path)
        if state:
            console.print(TITLE_ART)
            console.print("[dim]Save file found. Resuming session...[/dim]")
            console.print(
                f"[dim]Act {state.act} | Server: {state.current_server} | "
                f"Files read: {len(state.files_read)} | "
                f"Play time: {int(state.play_time_minutes())}m[/dim]"
            )
            console.print()
        else:
            console.print("[yellow]Save file corrupted. Starting new game.[/yellow]")
            args.new = True

    if state is None:
        # New game
        console.print(TITLE_ART)

        if not args.skip_intro:
            console.print("[dim]Press Enter to begin...[/dim]")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                return

        # Create game world
        create_game_world(data_dir, game_dir)
        state = GameState()

        if not args.skip_intro:
            boot_sequence()

    # Launch the shell
    shell = GameShell(game_dir, data_dir, state)

    try:
        shell.run()
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {e}[/bold red]")
        console.print("[dim]Your progress has been auto-saved.[/dim]")
        shell._auto_save()
        raise


if __name__ == "__main__":
    main()
