"""Utility commands: diff, echo, clear, help, hint, history, whoami, head, tail, wc, sort, uniq."""

from __future__ import annotations

import difflib
import os
from pathlib import Path

from neonvoid.engine.commands.base import CommandContext


class DiffCommand:
    name = "diff"
    aliases = []
    help_text = "Compare two files. Usage: diff <file1> <file2>"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        unified = False
        file_args: list[str] = []

        for arg in args:
            if arg in ("-u", "--unified"):
                unified = True
            elif not arg.startswith("-"):
                file_args.append(arg)

        if len(file_args) < 2:
            return "diff: missing operand"

        try:
            path1 = ctx.sandbox.resolve(file_args[0], ctx.cwd)
            path2 = ctx.sandbox.resolve(file_args[1], ctx.cwd)
        except PermissionError:
            return "diff: Permission denied"

        for p, name in [(path1, file_args[0]), (path2, file_args[1])]:
            if not p.exists():
                return f"diff: {name}: No such file or directory"
            if p.is_dir():
                return f"diff: {name}: Is a directory"

        try:
            lines1 = path1.read_text(errors="replace").splitlines(keepends=True)
            lines2 = path2.read_text(errors="replace").splitlines(keepends=True)
        except PermissionError:
            return "diff: Permission denied"

        if unified:
            result = difflib.unified_diff(
                lines1, lines2,
                fromfile=file_args[0], tofile=file_args[1],
            )
        else:
            result = difflib.unified_diff(
                lines1, lines2,
                fromfile=file_args[0], tofile=file_args[1],
            )

        output = ""
        for line in result:
            line = line.rstrip("\n")
            if line.startswith("+") and not line.startswith("+++"):
                output += f"[green]{line}[/green]\n"
            elif line.startswith("-") and not line.startswith("---"):
                output += f"[red]{line}[/red]\n"
            elif line.startswith("@@"):
                output += f"[cyan]{line}[/cyan]\n"
            else:
                output += f"{line}\n"

        if not output:
            return "[dim]Files are identical.[/dim]"
        return output.rstrip()


class EchoCommand:
    name = "echo"
    aliases = []
    help_text = "Display text. Usage: echo <text>"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        return " ".join(args)


class ClearCommand:
    name = "clear"
    aliases = ["cls"]
    help_text = "Clear the terminal screen."

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        return "__CLEAR__"


class HelpCommand:
    name = "help"
    aliases = ["?", "commands"]
    help_text = "Show available commands."

    def __init__(self, registry=None):
        self._registry = registry

    def set_registry(self, registry):
        self._registry = registry

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if self._registry is None:
            return "Help system unavailable."

        if args:
            # Help for specific command
            cmd = self._registry.get(args[0])
            if cmd:
                return f"[bold]{cmd.name}[/bold]: {cmd.help_text}"
            return f"help: no help for '{args[0]}'"

        lines = [
            "[bold cyan]NEXUS-7 TERMINAL - COMMAND REFERENCE[/bold cyan]",
            "[dim]Type 'help <command>' for details[/dim]\n",
        ]
        for cmd in self._registry.all_commands():
            aliases = f" [dim]({', '.join(cmd.aliases)})[/dim]" if cmd.aliases else ""
            lines.append(f"  [bold]{cmd.name:12}[/bold] {cmd.help_text}{aliases}")

        lines.append("\n[dim]Pipes: cmd1 | cmd2    Redirect: cmd > file[/dim]")
        return "\n".join(lines)


class HintCommand:
    name = "hint"
    aliases = ["stuck"]
    help_text = "Get a contextual hint if you're stuck."

    def __init__(self, hint_system=None):
        self._hint_system = hint_system

    def set_hint_system(self, hint_system):
        self._hint_system = hint_system

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if self._hint_system is None:
            return "[dim]Hint system initializing...[/dim]"
        return self._hint_system.get_hint(ctx.state)


class WhoamiCommand:
    name = "whoami"
    aliases = []
    help_text = "Display current user."

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if ctx.state.current_server == "local":
            return "kai.voss"
        return f"kai@{ctx.state.current_server}"


class HeadCommand:
    name = "head"
    aliases = []
    help_text = "Show first lines of a file. Usage: head [-n NUM] <file>"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        num_lines = 10
        file_arg: str | None = None

        i = 0
        while i < len(args):
            if args[i] == "-n" and i + 1 < len(args):
                try:
                    num_lines = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif not args[i].startswith("-"):
                file_arg = args[i]
                i += 1
            else:
                i += 1

        # Pipe input
        if file_arg is None and ctx.pipe_input is not None:
            lines = ctx.pipe_input.splitlines()[:num_lines]
            return "\n".join(lines)

        if file_arg is None:
            return "head: missing file operand"

        try:
            path = ctx.sandbox.resolve(file_arg, ctx.cwd)
        except PermissionError:
            return f"head: {file_arg}: Permission denied"

        if not path.exists():
            return f"head: {file_arg}: No such file or directory"

        try:
            content = path.read_text(errors="replace")
            lines = content.splitlines()[:num_lines]
            return "\n".join(lines)
        except PermissionError:
            return f"head: {file_arg}: Permission denied"


class TailCommand:
    name = "tail"
    aliases = []
    help_text = "Show last lines of a file. Usage: tail [-n NUM] <file>"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        num_lines = 10
        file_arg: str | None = None

        i = 0
        while i < len(args):
            if args[i] == "-n" and i + 1 < len(args):
                try:
                    num_lines = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif not args[i].startswith("-"):
                file_arg = args[i]
                i += 1
            else:
                i += 1

        if file_arg is None and ctx.pipe_input is not None:
            lines = ctx.pipe_input.splitlines()[-num_lines:]
            return "\n".join(lines)

        if file_arg is None:
            return "tail: missing file operand"

        try:
            path = ctx.sandbox.resolve(file_arg, ctx.cwd)
        except PermissionError:
            return f"tail: {file_arg}: Permission denied"

        if not path.exists():
            return f"tail: {file_arg}: No such file or directory"

        try:
            content = path.read_text(errors="replace")
            lines = content.splitlines()[-num_lines:]
            return "\n".join(lines)
        except PermissionError:
            return f"tail: {file_arg}: Permission denied"


class WcCommand:
    name = "wc"
    aliases = []
    help_text = "Count lines, words, and characters. Usage: wc [-lwc] <file>"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        file_args: list[str] = []
        flags = set()

        for arg in args:
            if arg.startswith("-"):
                for ch in arg[1:]:
                    flags.add(ch)
            else:
                file_args.append(arg)

        if not flags:
            flags = {"l", "w", "c"}

        text: str | None = None
        label = ""

        if not file_args and ctx.pipe_input is not None:
            text = ctx.pipe_input
        elif file_args:
            try:
                path = ctx.sandbox.resolve(file_args[0], ctx.cwd)
                text = path.read_text(errors="replace")
                label = f" {file_args[0]}"
            except (PermissionError, OSError) as e:
                return f"wc: {file_args[0]}: {e}"
        else:
            return "wc: missing file operand"

        parts: list[str] = []
        if "l" in flags:
            parts.append(str(text.count("\n")))
        if "w" in flags:
            parts.append(str(len(text.split())))
        if "c" in flags:
            parts.append(str(len(text)))

        return "  ".join(parts) + label


class SortCommand:
    name = "sort"
    aliases = []
    help_text = "Sort lines. Usage: sort [file]"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        reverse = "-r" in args
        file_args = [a for a in args if not a.startswith("-")]

        if not file_args and ctx.pipe_input is not None:
            lines = ctx.pipe_input.splitlines()
        elif file_args:
            try:
                path = ctx.sandbox.resolve(file_args[0], ctx.cwd)
                lines = path.read_text(errors="replace").splitlines()
            except (PermissionError, OSError) as e:
                return f"sort: {e}"
        else:
            return ""

        lines.sort(reverse=reverse)
        return "\n".join(lines)


class UniqCommand:
    name = "uniq"
    aliases = []
    help_text = "Filter duplicate lines. Usage: uniq [file]"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        count = "-c" in args
        file_args = [a for a in args if not a.startswith("-")]

        if not file_args and ctx.pipe_input is not None:
            lines = ctx.pipe_input.splitlines()
        elif file_args:
            try:
                path = ctx.sandbox.resolve(file_args[0], ctx.cwd)
                lines = path.read_text(errors="replace").splitlines()
            except (PermissionError, OSError) as e:
                return f"uniq: {e}"
        else:
            return ""

        result: list[str] = []
        prev = None
        cnt = 0
        for line in lines:
            if line == prev:
                cnt += 1
            else:
                if prev is not None:
                    if count:
                        result.append(f"  {cnt} {prev}")
                    else:
                        result.append(prev)
                prev = line
                cnt = 1
        if prev is not None:
            if count:
                result.append(f"  {cnt} {prev}")
            else:
                result.append(prev)

        return "\n".join(result)
