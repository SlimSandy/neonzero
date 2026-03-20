"""Filesystem commands: ls, cd, pwd, cat, find, chmod."""

from __future__ import annotations

import os
import stat
from fnmatch import fnmatch
from pathlib import Path

from neonvoid.engine.commands.base import CommandContext


class LsCommand:
    name = "ls"
    aliases = ["dir"]
    help_text = "List directory contents. Usage: ls [-la] [path]"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        show_hidden = False
        show_long = False
        show_recursive = False
        paths: list[str] = []

        for arg in args:
            if arg.startswith("-"):
                if "a" in arg:
                    show_hidden = True
                if "l" in arg:
                    show_long = True
                if "R" in arg:
                    show_recursive = True
            else:
                paths.append(arg)

        target = ctx.cwd
        if paths:
            target = ctx.sandbox.resolve(paths[0], ctx.cwd)

        if not target.exists():
            return f"ls: cannot access '{paths[0] if paths else '.'}': No such file or directory"
        if not target.is_dir():
            return self._format_entry(target, show_long, ctx)

        if show_recursive:
            return self._ls_recursive(target, show_hidden, show_long, ctx)

        return self._ls_dir(target, show_hidden, show_long, ctx)

    def _ls_dir(self, target: Path, show_hidden: bool, show_long: bool, ctx: CommandContext) -> str:
        entries = sorted(target.iterdir(), key=lambda p: p.name)
        if not show_hidden:
            entries = [e for e in entries if not e.name.startswith(".")]

        if not entries:
            return ""

        if show_long:
            lines = []
            for entry in entries:
                lines.append(self._format_entry(entry, True, ctx))
            return "\n".join(lines)
        else:
            names = []
            for entry in entries:
                name = entry.name
                if entry.is_dir():
                    name = f"[bold cyan]{name}/[/bold cyan]"
                elif entry.name.endswith((".sh", ".py")):
                    name = f"[bold green]{name}[/bold green]"
                elif entry.name.endswith((".enc", ".gz")):
                    name = f"[yellow]{name}[/yellow]"
                elif entry.name.endswith((".log", ".csv")):
                    name = f"[dim]{name}[/dim]"
                else:
                    name = f"{name}"
                names.append(name)
            return "  ".join(names)

    def _ls_recursive(self, target: Path, show_hidden: bool, show_long: bool, ctx: CommandContext) -> str:
        lines = []
        for root, dirs, files in os.walk(target):
            root_path = Path(root)
            if not show_hidden:
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                files = [f for f in files if not f.startswith(".")]

            rel = ctx.sandbox.relative_display(root_path)
            lines.append(f"\n{rel}:")
            entries = sorted(
                [root_path / d for d in dirs] + [root_path / f for f in files],
                key=lambda p: p.name,
            )
            for entry in entries:
                lines.append(self._format_entry(entry, show_long, ctx))
        return "\n".join(lines)

    def _format_entry(self, entry: Path, long_format: bool, ctx: CommandContext) -> str:
        name = entry.name
        if entry.is_dir():
            name = f"[bold cyan]{name}/[/bold cyan]"
        elif entry.name.endswith((".sh", ".py")):
            name = f"[bold green]{name}[/bold green]"

        if not long_format:
            return name

        try:
            st = entry.stat()
            perms = stat.filemode(st.st_mode)
            size = st.st_size
            return f"{perms}  {size:>8}  {name}"
        except OSError:
            return f"??????????         ?  {name}"


class CdCommand:
    name = "cd"
    aliases = []
    help_text = "Change directory. Usage: cd [path]"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if not args or args[0] in ("~", ""):
            ctx.new_cwd = ctx.game_root / ctx.state.current_server
            return ""

        if args[0] == "-":
            return "cd: OLDPWD not set"

        try:
            target = ctx.sandbox.resolve(args[0], ctx.cwd)
        except PermissionError:
            return f"cd: access denied"

        if not target.exists():
            return f"cd: {args[0]}: No such file or directory"
        if not target.is_dir():
            return f"cd: {args[0]}: Not a directory"

        ctx.new_cwd = target
        return ""


class PwdCommand:
    name = "pwd"
    aliases = []
    help_text = "Print working directory."

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        return ctx.sandbox.relative_display(ctx.cwd)


class CatCommand:
    name = "cat"
    aliases = ["less", "more"]
    help_text = "Display file contents. Usage: cat <file> [file2 ...]"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if not args:
            # If we have pipe input, pass it through
            if ctx.pipe_input is not None:
                return ctx.pipe_input
            return "cat: missing file operand"

        outputs: list[str] = []
        for arg in args:
            if arg.startswith("-"):
                continue
            try:
                path = ctx.sandbox.resolve(arg, ctx.cwd)
            except PermissionError:
                outputs.append(f"cat: {arg}: Permission denied")
                continue

            if not path.exists():
                outputs.append(f"cat: {arg}: No such file or directory")
                continue
            if path.is_dir():
                outputs.append(f"cat: {arg}: Is a directory")
                continue

            try:
                # Check read permissions
                if not os.access(path, os.R_OK):
                    outputs.append(f"cat: {arg}: Permission denied")
                    continue
                content = path.read_text(errors="replace")
                outputs.append(content)
                # Record file read for game state tracking
                rel_path = str(path.relative_to(ctx.game_root))
                ctx.state.record_file_read(rel_path)
            except PermissionError:
                outputs.append(f"cat: {arg}: Permission denied")
            except Exception:
                outputs.append(f"cat: {arg}: Error reading file")

        return "\n".join(outputs)


class FindCommand:
    name = "find"
    aliases = []
    help_text = "Find files. Usage: find [path] -name <pattern> [-type f|d]"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        search_path = ctx.cwd
        name_pattern: str | None = None
        type_filter: str | None = None

        i = 0
        while i < len(args):
            if args[i] == "-name" and i + 1 < len(args):
                name_pattern = args[i + 1]
                i += 2
            elif args[i] == "-type" and i + 1 < len(args):
                type_filter = args[i + 1]
                i += 2
            elif args[i] == "-iname" and i + 1 < len(args):
                name_pattern = args[i + 1]
                i += 2
            elif not args[i].startswith("-"):
                try:
                    search_path = ctx.sandbox.resolve(args[i], ctx.cwd)
                except PermissionError:
                    return f"find: '{args[i]}': Permission denied"
                i += 1
            else:
                i += 1

        if not search_path.exists():
            return f"find: '{search_path}': No such file or directory"

        results: list[str] = []
        for root, dirs, files in os.walk(search_path):
            root_path = Path(root)
            entries = []
            if type_filter != "f":
                entries.extend((root_path / d, True) for d in dirs)
            if type_filter != "d":
                entries.extend((root_path / f, False) for f in files)

            for entry_path, is_dir in entries:
                if name_pattern:
                    if not fnmatch(entry_path.name, name_pattern):
                        continue
                rel = ctx.sandbox.relative_display(entry_path)
                results.append(rel)

        if not results:
            return ""
        return "\n".join(sorted(results))


class ChmodCommand:
    name = "chmod"
    aliases = []
    help_text = "Change file permissions. Usage: chmod <mode> <file>"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if len(args) < 2:
            return "chmod: missing operand"

        mode_str = args[0]
        recursive = False
        file_args = args[1:]

        if mode_str == "-R" and len(args) >= 3:
            recursive = True
            mode_str = args[1]
            file_args = args[2:]

        for file_arg in file_args:
            try:
                path = ctx.sandbox.resolve(file_arg, ctx.cwd)
            except PermissionError:
                return f"chmod: '{file_arg}': Permission denied"

            if not path.exists():
                return f"chmod: cannot access '{file_arg}': No such file or directory"

            try:
                new_mode = self._parse_mode(mode_str, path)
                os.chmod(path, new_mode)
            except ValueError as e:
                return f"chmod: invalid mode: '{mode_str}'"
            except OSError as e:
                return f"chmod: changing permissions of '{file_arg}': {e}"

        return ""

    def _parse_mode(self, mode_str: str, path: Path) -> int:
        """Parse chmod mode string (octal or symbolic).

        Supports:
            Octal:    644, 755, 0644, etc.
            Symbolic: +r, u+r, a+rx, go-w, u+rw, etc.
        """
        # Try octal first
        try:
            return int(mode_str, 8)
        except ValueError:
            pass

        # Symbolic mode: [ugoa]*[+-][rwx]+
        # Examples: +r, u+r, a+rx, go-w, u+rw, +rwx
        current = path.stat().st_mode

        # Split on each +/- operation (supports chained like u+r,g+w but
        # we'll handle the simple common cases)
        for clause in mode_str.split(","):
            clause = clause.strip()
            if not clause:
                continue

            # Find the operator (+ or -)
            op_idx = -1
            for i, ch in enumerate(clause):
                if ch in "+-=":
                    op_idx = i
                    break

            if op_idx < 0:
                raise ValueError(f"Unsupported mode: {mode_str}")

            who = clause[:op_idx] if op_idx > 0 else "a"
            operator = clause[op_idx]
            perms = clause[op_idx + 1:]

            if not perms:
                raise ValueError(f"Unsupported mode: {mode_str}")

            # Validate 'who' characters
            if not all(c in "ugoa" for c in who):
                raise ValueError(f"Unsupported mode: {mode_str}")

            # Build the bitmask for the specified permissions
            mask = 0
            for p in perms:
                if p == "r":
                    if "u" in who or "a" in who:
                        mask |= stat.S_IRUSR
                    if "g" in who or "a" in who:
                        mask |= stat.S_IRGRP
                    if "o" in who or "a" in who:
                        mask |= stat.S_IROTH
                elif p == "w":
                    if "u" in who or "a" in who:
                        mask |= stat.S_IWUSR
                    if "g" in who or "a" in who:
                        mask |= stat.S_IWGRP
                    if "o" in who or "a" in who:
                        mask |= stat.S_IWOTH
                elif p == "x":
                    if "u" in who or "a" in who:
                        mask |= stat.S_IXUSR
                    if "g" in who or "a" in who:
                        mask |= stat.S_IXGRP
                    if "o" in who or "a" in who:
                        mask |= stat.S_IXOTH
                else:
                    raise ValueError(f"Unsupported mode: {mode_str}")

            if operator == "+":
                current |= mask
            elif operator == "-":
                current &= ~mask
            elif operator == "=":
                # Clear existing bits for the specified who, then set
                clear_mask = 0
                if "u" in who or "a" in who:
                    clear_mask |= stat.S_IRWXU
                if "g" in who or "a" in who:
                    clear_mask |= stat.S_IRWXG
                if "o" in who or "a" in who:
                    clear_mask |= stat.S_IRWXO
                current = (current & ~clear_mask) | mask

        return current
