"""Search commands: grep."""

from __future__ import annotations

import os
import re
from pathlib import Path

from neonvoid.engine.commands.base import CommandContext


class GrepCommand:
    name = "grep"
    aliases = []
    help_text = "Search file contents. Usage: grep [-rinl] <pattern> [file/dir ...]"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        case_insensitive = False
        recursive = False
        show_line_nums = False
        files_only = False
        invert = False
        pattern: str | None = None
        targets: list[str] = []

        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("-") and not arg.startswith("--") and len(arg) > 1:
                for ch in arg[1:]:
                    if ch == "i":
                        case_insensitive = True
                    elif ch == "r":
                        recursive = True
                    elif ch == "n":
                        show_line_nums = True
                    elif ch == "l":
                        files_only = True
                    elif ch == "v":
                        invert = True
            elif arg == "--":
                # Everything after is positional
                targets.extend(args[i + 1:])
                break
            elif pattern is None:
                pattern = arg
            else:
                targets.append(arg)
            i += 1

        if pattern is None:
            # Check pipe input
            if ctx.pipe_input is not None and args:
                pattern = args[0]
                return self._grep_text(ctx.pipe_input, pattern, case_insensitive, show_line_nums, invert)
            return "grep: missing pattern"

        # If pipe input and no targets, grep pipe input
        if not targets and ctx.pipe_input is not None:
            return self._grep_text(ctx.pipe_input, pattern, case_insensitive, show_line_nums, invert)

        # If no targets and no pipe, grep current dir recursively
        if not targets:
            if recursive:
                targets = ["."]
            else:
                return "grep: missing file operand"

        flags = re.IGNORECASE if case_insensitive else 0
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return f"grep: invalid regex '{pattern}': {e}"

        results: list[str] = []
        files_to_search: list[Path] = []

        for target in targets:
            try:
                path = ctx.sandbox.resolve(target, ctx.cwd)
            except PermissionError:
                results.append(f"grep: '{target}': Permission denied")
                continue

            if not path.exists():
                results.append(f"grep: {target}: No such file or directory")
                continue

            if path.is_dir():
                if recursive:
                    for root, _, filenames in os.walk(path):
                        for fn in filenames:
                            fp = Path(root) / fn
                            if ctx.sandbox.is_within(fp):
                                files_to_search.append(fp)
                else:
                    results.append(f"grep: {target}: Is a directory")
            else:
                files_to_search.append(path)

        multi_file = len(files_to_search) > 1 or recursive
        matched_files: set[str] = set()

        for fp in sorted(files_to_search):
            try:
                if not os.access(fp, os.R_OK):
                    continue
                content = fp.read_text(errors="replace")
            except (PermissionError, OSError):
                continue

            rel = ctx.sandbox.relative_display(fp)

            for line_num, line in enumerate(content.splitlines(), 1):
                match = regex.search(line)
                if (match and not invert) or (not match and invert):
                    if files_only:
                        if rel not in matched_files:
                            matched_files.add(rel)
                            results.append(rel)
                    elif multi_file:
                        prefix = f"[cyan]{rel}[/cyan]:"
                        if show_line_nums:
                            prefix += f"[dim]{line_num}[/dim]:"
                        # Highlight the match
                        highlighted = regex.sub(
                            lambda m: f"[bold red]{m.group()}[/bold red]",
                            line,
                        )
                        results.append(f"{prefix}{highlighted}")
                    else:
                        if show_line_nums:
                            prefix = f"[dim]{line_num}[/dim]:"
                        else:
                            prefix = ""
                        highlighted = regex.sub(
                            lambda m: f"[bold red]{m.group()}[/bold red]",
                            line,
                        )
                        results.append(f"{prefix}{highlighted}")

        return "\n".join(results)

    def _grep_text(
        self, text: str, pattern: str, case_insensitive: bool,
        show_line_nums: bool, invert: bool,
    ) -> str:
        """Grep through piped text input."""
        flags = re.IGNORECASE if case_insensitive else 0
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return f"grep: invalid regex '{pattern}': {e}"

        results: list[str] = []
        for line_num, line in enumerate(text.splitlines(), 1):
            match = regex.search(line)
            if (match and not invert) or (not match and invert):
                if show_line_nums:
                    prefix = f"[dim]{line_num}[/dim]:"
                else:
                    prefix = ""
                highlighted = regex.sub(
                    lambda m: f"[bold red]{m.group()}[/bold red]",
                    line,
                )
                results.append(f"{prefix}{highlighted}")

        return "\n".join(results)
