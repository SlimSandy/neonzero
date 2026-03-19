"""Custom REPL shell - the heart of the game engine."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style

from neonvoid.engine.commands.base import CommandContext, CommandRegistry
from neonvoid.engine.commands.filesystem import (
    CatCommand, CdCommand, ChmodCommand, FindCommand, LsCommand, PwdCommand,
)
from neonvoid.engine.commands.search import GrepCommand
from neonvoid.engine.commands.archive import TarCommand
from neonvoid.engine.commands.network import (
    CurlCommand, ExitCommand, PingCommand, SshCommand,
)
from neonvoid.engine.commands.utility import (
    ClearCommand, DiffCommand, EchoCommand, HeadCommand, HelpCommand,
    HintCommand, SortCommand, TailCommand, UniqCommand, WcCommand, WhoamiCommand,
)
from neonvoid.engine.parser import parse_input
from neonvoid.engine.sandbox import Sandbox
from neonvoid.engine.world import create_escape_directory, create_server_filesystem
from neonvoid.game.events import build_triggers
from neonvoid.game.hints import HintSystem
from neonvoid.game.progression import (
    check_act_progression, get_act_intro_text, should_unlock_escape,
)
from neonvoid.game.puzzles import check_door_override, check_firewall_bypass
from neonvoid.game.state import GameState
from neonvoid.story.narrative import NARRATIVES
from neonvoid.ui.effects import (
    discovery_effect, ending_sequence, ssh_connection_animation,
    ssh_disconnect_animation,
)
from neonvoid.ui.prompt import get_prompt, get_toolbar
from neonvoid.ui.terminal import console, print_narrative, print_output, print_system
from neonvoid.ui.credits import play_credits, play_post_credits
from neonvoid.ui.ascii import DOOR_OPEN

PROMPT_STYLE = Style.from_dict({
    "bottom-toolbar": "bg:#1a1a2e #888888",
})


class GameShell:
    """The main game shell - custom REPL that runs the game."""

    def __init__(self, game_dir: Path, data_dir: Path, state: GameState | None = None):
        self.game_dir = game_dir.resolve()
        self.data_dir = data_dir.resolve()
        self.state = state or GameState()
        self.sandbox = Sandbox(self.game_dir)
        self.cwd = self.game_dir / "local"
        self.registry = CommandRegistry()
        self.triggers = build_triggers()
        self.hint_system = HintSystem()
        self.running = True
        self._previous_server_cwds: dict[str, Path] = {}

        self._register_commands()

        self.session = PromptSession(
            history=InMemoryHistory(),
            style=PROMPT_STYLE,
            completer=self._make_completer(),
        )

    def _register_commands(self):
        """Register all available commands."""
        help_cmd = HelpCommand()
        hint_cmd = HintCommand()

        commands = [
            LsCommand(), CdCommand(), PwdCommand(), CatCommand(),
            FindCommand(), ChmodCommand(), GrepCommand(), TarCommand(),
            SshCommand(), ExitCommand(), PingCommand(), CurlCommand(),
            DiffCommand(), EchoCommand(), ClearCommand(), help_cmd,
            hint_cmd, WhoamiCommand(), HeadCommand(), TailCommand(),
            WcCommand(), SortCommand(), UniqCommand(),
        ]

        for cmd in commands:
            self.registry.register(cmd)

        help_cmd.set_registry(self.registry)
        hint_cmd.set_hint_system(self.hint_system)

    def _make_completer(self):
        """Create a path completer that works within the sandbox."""
        return PathCompleter(expanduser=False, get_paths=lambda: [str(self.cwd)])

    def run(self):
        """Main game loop."""
        while self.running:
            try:
                prompt = get_prompt(self.state, self.cwd, self.sandbox)
                toolbar = get_toolbar(self.state)

                raw_input = self.session.prompt(
                    prompt,
                    bottom_toolbar=toolbar,
                )

                if not raw_input.strip():
                    continue

                self._execute(raw_input.strip())

            except KeyboardInterrupt:
                console.print("\n[dim]Use 'exit' to disconnect or Ctrl+D to quit.[/dim]")
            except EOFError:
                self._handle_quit()
                break

    def _execute(self, raw_input: str):
        """Execute a command line (possibly with pipes)."""
        # Handle special game commands first
        if raw_input.startswith("firewall-ctl"):
            self._handle_firewall_ctl(raw_input)
            return

        if raw_input.startswith("./override.sh"):
            self._handle_door_override(raw_input)
            return

        if raw_input in ("quit", "q"):
            self._handle_quit()
            return

        if raw_input == "save":
            self._save_game()
            return

        pipeline = parse_input(raw_input)

        if not pipeline.commands:
            return

        # Execute pipeline
        pipe_output: str | None = None

        for parsed_cmd in pipeline.commands:
            cmd = self.registry.get(parsed_cmd.name)
            if cmd is None:
                print_output(f"[red]{parsed_cmd.name}: command not found[/red]")
                return

            ctx = CommandContext(
                cwd=self.cwd,
                game_root=self.game_dir,
                sandbox=self.sandbox,
                state=self.state,
                pipe_input=pipe_output,
            )

            try:
                output = cmd.execute(parsed_cmd.args, ctx)
            except Exception as e:
                print_output(f"[red]Error: {e}[/red]")
                return

            self.state.record_command(parsed_cmd.name)

            # Handle cwd changes
            if ctx.new_cwd is not None:
                self.cwd = ctx.new_cwd

            # Handle special actions
            if ctx.action:
                self._handle_action(ctx.action, ctx.action_data or {})
                if ctx.action.startswith("ending_"):
                    return

            # Handle special output markers
            if output.startswith("__SSH_CONNECT__"):
                server = output.replace("__SSH_CONNECT__", "")
                self._handle_ssh_connect(server, ctx.action_data or {})
                return
            elif output == "__SSH_DISCONNECT__":
                self._handle_ssh_disconnect()
                return
            elif output == "__CLEAR__":
                console.clear()
                return
            elif output.startswith("__ENDING_"):
                return  # Already handled by action

            pipe_output = output

            # Check triggers after each command
            self._check_triggers(parsed_cmd.name, parsed_cmd.args, output)

        # Print final output
        if pipe_output:
            # Handle redirect
            if pipeline.redirect_to:
                self._redirect_output(pipe_output, pipeline.redirect_to)
            else:
                print_output(pipe_output)

        # Check progression
        self._check_progression()

    def _check_triggers(self, cmd: str, args: list[str], output: str):
        """Check all triggers against the current command."""
        for trigger in self.triggers:
            if trigger.check(self.state, cmd, args, output):
                trigger.apply(self.state)
                if trigger.narrative_key and trigger.narrative_key in NARRATIVES:
                    print_narrative(NARRATIVES[trigger.narrative_key])

    def _check_progression(self):
        """Check if the player should advance to a new act."""
        new_act = check_act_progression(self.state)
        if new_act is not None and new_act != self.state.act:
            self.state.act = new_act
            intro = get_act_intro_text(new_act)
            if intro:
                print_narrative(intro)

        # Check if escape directory should be created
        if should_unlock_escape(self.state):
            create_escape_directory(self.data_dir, self.game_dir)
            self.state.set_flag("escape_unlocked")
            print_system(
                "[yellow]SYSTEM ALERT: New directory detected in lab-9 filesystem.[/yellow]\n"
                "[dim]Something has been unlocked...[/dim]"
            )

    def _handle_ssh_connect(self, server: str, data: dict):
        """Handle SSH connection to a server."""
        user = data.get("user", "kai")

        # Save current cwd for this server
        self._previous_server_cwds[self.state.current_server] = self.cwd

        # Create server filesystem if needed
        create_server_filesystem(server, self.data_dir, self.game_dir)

        # Play animation
        ssh_connection_animation(server, user)

        # Switch to server
        self.state.current_server = server
        self.state.set_flag(data.get("server_flag", ""))
        self.cwd = self.game_dir / server

        # Check triggers and progression
        self._check_triggers("ssh", [f"{user}@{server}"], f"__SSH_CONNECT__{server}")
        self._check_progression()

    def _handle_ssh_disconnect(self):
        """Handle disconnecting from a server."""
        old_server = self.state.current_server
        ssh_disconnect_animation(old_server)

        # Return to local
        self.state.current_server = "local"
        self.cwd = self._previous_server_cwds.get("local", self.game_dir / "local")

    def _handle_action(self, action: str, data: dict):
        """Handle special actions from commands."""
        if action == "ending_a":
            self._play_ending("A")
        elif action == "ending_b":
            self._play_ending("B")
        elif action == "ending_c":
            self._play_ending("C")

    def _handle_firewall_ctl(self, raw_input: str):
        """Handle the firewall-ctl command."""
        parts = raw_input.split()[1:] if len(raw_input.split()) > 1 else []
        success, output = check_firewall_bypass(parts, self.state)
        print_output(output)
        if success:
            self._check_triggers("firewall-ctl", parts, output)
            print_narrative(
                "The firewall rule drops. The archive server, once sealed behind "
                "Director Sable's order, is now reachable. Whatever secrets they "
                "locked away in deep storage are waiting.\n\n"
                "[dim italic]River said the proof was there. Time to find out.[/dim italic]"
            )

    def _handle_door_override(self, raw_input: str):
        """Handle the door override script."""
        parts = raw_input.replace("./override.sh", "").strip().split()
        success, output = check_door_override(parts, self.state)

        if success:
            discovery_effect("DOOR LOCK DISENGAGED")
            console.print(DOOR_OPEN)
            print_narrative(NARRATIVES.get("door_unlocked", "The door is open."))
            self._auto_save()
        else:
            print_output(output)

    def _play_ending(self, ending: str):
        """Play an ending sequence."""
        self.state.ending = ending
        self.state.escaped = True
        self.state.end_time = __import__("time").time()

        narrative_key = f"ending_{ending.lower()}"
        text = NARRATIVES.get(narrative_key, "You escape.")

        ending_sequence(ending, text)
        play_credits(self.state)
        play_post_credits()

        self._auto_save()
        self.running = False

    def _handle_quit(self):
        """Handle quitting the game."""
        if self.state.current_server != "local":
            # Disconnect first
            self._handle_ssh_disconnect()
            return

        self._auto_save()
        console.print("\n[dim]Session terminated. Progress saved.[/dim]")
        console.print("[dim]Run 'neonvoid' to continue your session.[/dim]\n")
        self.running = False

    def _redirect_output(self, output: str, filename: str):
        """Redirect output to a file in the game filesystem."""
        try:
            path = self.sandbox.resolve(filename, self.cwd)
            # Strip Rich markup for file output
            import re
            clean = re.sub(r'\[/?[^\]]+\]', '', output)
            path.write_text(clean)
            print_system(f"Output written to {filename}")
        except PermissionError:
            print_output(f"[red]Permission denied: {filename}[/red]")
        except Exception as e:
            print_output(f"[red]Error writing to {filename}: {e}[/red]")

    def _save_game(self):
        """Save the game state."""
        self._auto_save()
        print_system("Game saved.")

    def _auto_save(self):
        """Auto-save game state."""
        save_path = self.game_dir / ".save" / "state.json"
        self.state.save(save_path)
