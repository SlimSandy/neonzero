"""Archive commands: tar."""

from __future__ import annotations

import tarfile
from pathlib import Path

from neonvoid.engine.commands.base import CommandContext


class TarCommand:
    name = "tar"
    aliases = []
    help_text = "Extract archives. Usage: tar xzf <archive.tar.gz>"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if not args:
            return "tar: missing operand"

        # Parse flags
        extract = False
        gzip = False
        verbose = False
        archive_path: str | None = None
        change_dir: str | None = None

        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("-") or (i == 0 and not arg.startswith("/")):
                flags = arg.lstrip("-")
                for ch in flags:
                    if ch == "x":
                        extract = True
                    elif ch == "z":
                        gzip = True
                    elif ch == "v":
                        verbose = True
                    elif ch == "f":
                        # Next arg is the file
                        if i + 1 < len(args):
                            i += 1
                            archive_path = args[i]
                        else:
                            return "tar: option requires an argument -- 'f'"
                    elif ch == "C":
                        if i + 1 < len(args):
                            i += 1
                            change_dir = args[i]
                if archive_path is None and i == 0:
                    # Flags without -f, next positional is the archive
                    pass
            elif archive_path is None:
                archive_path = arg
            i += 1

        if not extract:
            return "tar: only extraction (x) is supported in this terminal"

        if archive_path is None:
            return "tar: no archive file specified"

        try:
            path = ctx.sandbox.resolve(archive_path, ctx.cwd)
        except PermissionError:
            return f"tar: {archive_path}: Permission denied"

        if not path.exists():
            return f"tar: {archive_path}: No such file or directory"

        # Determine extraction directory
        if change_dir:
            try:
                extract_to = ctx.sandbox.resolve(change_dir, ctx.cwd)
            except PermissionError:
                return f"tar: {change_dir}: Permission denied"
        else:
            extract_to = ctx.cwd

        try:
            with tarfile.open(path, "r:gz" if gzip or path.name.endswith(".gz") else "r") as tf:
                # Security: check for path traversal in archive
                for member in tf.getmembers():
                    member_path = (extract_to / member.name).resolve()
                    if not ctx.sandbox.is_within(member_path):
                        return "tar: archive contains files that escape the sandbox -- aborting"

                tf.extractall(path=extract_to, filter="data")

                if verbose:
                    members = tf.getnames()
                    return "\n".join(members)
                else:
                    return f"Extracted to {ctx.sandbox.relative_display(extract_to)}"
        except tarfile.TarError as e:
            return f"tar: error extracting '{archive_path}': {e}"
        except Exception as e:
            return f"tar: {e}"
