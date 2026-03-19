"""Dynamic prompt styling for the custom shell."""

from __future__ import annotations

from pathlib import Path

from prompt_toolkit.formatted_text import HTML

from neonvoid.engine.sandbox import Sandbox
from neonvoid.game.state import GameState

# Server colors for the prompt
SERVER_COLORS = {
    "local": "#00ff88",
    "nexus-core": "#00ccff",
    "archive": "#ffcc00",
    "lab-9": "#ff3333",
}


def get_prompt(state: GameState, cwd: Path, sandbox: Sandbox) -> HTML:
    """Generate the prompt based on current game state."""
    server = state.current_server
    color = SERVER_COLORS.get(server, "#ffffff")
    user = "kai"
    rel_path = sandbox.relative_display(cwd)

    # Build prompt: user@server:path$
    return HTML(
        f'<style fg="{color}" bold="true">{user}@{server}</style>'
        f'<style fg="#888888">:</style>'
        f'<style fg="#aaaaaa">{rel_path}</style>'
        f'<style fg="#888888">$ </style>'
    )


def get_toolbar(state: GameState) -> HTML:
    """Generate the bottom toolbar text."""
    server = state.current_server
    color = SERVER_COLORS.get(server, "#ffffff")
    act = state.act

    act_names = {
        1: "WHO AM I?",
        2: "WHAT HAPPENED?",
        3: "WHAT AM I?",
        4: "ESCAPE",
    }
    act_name = act_names.get(act, "???")

    minutes = int(state.play_time_minutes())
    time_str = f"{minutes}m"

    cmds = len(state.commands_used)
    files = len(state.files_read)

    return HTML(
        f' <style fg="{color}">[ {server.upper()} ]</style>'
        f'  <style fg="#666666">Act {act}: {act_name}</style>'
        f'  <style fg="#444444">|</style>'
        f'  <style fg="#666666">{time_str}</style>'
        f'  <style fg="#444444">|</style>'
        f'  <style fg="#666666">{cmds} cmds / {files} files</style>'
        f'  <style fg="#444444">| hint for help</style>'
    )
