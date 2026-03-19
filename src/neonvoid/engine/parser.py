"""Command parser - handles pipes, quoting, and argument splitting."""

from __future__ import annotations

import shlex
from dataclasses import dataclass, field


@dataclass
class ParsedCommand:
    """A single command with its arguments."""
    name: str
    args: list[str] = field(default_factory=list)
    raw: str = ""


@dataclass
class Pipeline:
    """A sequence of commands connected by pipes."""
    commands: list[ParsedCommand] = field(default_factory=list)
    redirect_to: str | None = None  # Output file for > redirect


def parse_input(raw_input: str) -> Pipeline:
    """Parse a command line into a Pipeline.

    Supports:
        - Pipes: cmd1 | cmd2 | cmd3
        - Output redirect: cmd > file
        - Quoted strings: cat "file with spaces"
        - Single and double quotes
    """
    raw_input = raw_input.strip()
    if not raw_input:
        return Pipeline()

    # Split on pipes first (respecting quotes)
    pipe_segments = _split_pipes(raw_input)

    commands: list[ParsedCommand] = []
    redirect_to: str | None = None

    for i, segment in enumerate(pipe_segments):
        segment = segment.strip()
        if not segment:
            continue

        # Check for output redirect on the last segment
        if i == len(pipe_segments) - 1:
            segment, redirect_to = _extract_redirect(segment)
            segment = segment.strip()
            if not segment:
                continue

        try:
            tokens = shlex.split(segment)
        except ValueError:
            # Unmatched quotes - try a simpler split
            tokens = segment.split()

        if not tokens:
            continue

        commands.append(ParsedCommand(
            name=tokens[0],
            args=tokens[1:],
            raw=segment,
        ))

    return Pipeline(commands=commands, redirect_to=redirect_to)


def _split_pipes(raw: str) -> list[str]:
    """Split a string on | characters, respecting quotes."""
    segments: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False
    escape = False

    for char in raw:
        if escape:
            current.append(char)
            escape = False
            continue

        if char == "\\":
            escape = True
            current.append(char)
            continue

        if char == "'" and not in_double:
            in_single = not in_single
            current.append(char)
        elif char == '"' and not in_single:
            in_double = not in_double
            current.append(char)
        elif char == "|" and not in_single and not in_double:
            segments.append("".join(current))
            current = []
        else:
            current.append(char)

    segments.append("".join(current))
    return segments


def _extract_redirect(segment: str) -> tuple[str, str | None]:
    """Extract > redirect from the end of a command segment.

    Returns (command_part, redirect_file_or_none).
    """
    in_single = False
    in_double = False

    for i, char in enumerate(segment):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == ">" and not in_single and not in_double:
            command_part = segment[:i].strip()
            file_part = segment[i + 1:].strip()
            # Handle >> (append) - treat as > for simplicity
            if file_part.startswith(">"):
                file_part = file_part[1:].strip()
            return command_part, file_part if file_part else None

    return segment, None
