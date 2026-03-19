"""End credits sequence."""

from __future__ import annotations

import time

from neonvoid.ui.terminal import console
from neonvoid.ui.effects import typewriter


def play_credits(state):
    """Play the end credits with stats."""
    console.clear()
    time.sleep(1)

    console.print()
    console.print("[bold cyan]N E O N   V O I D[/bold cyan]", justify="center")
    console.print("[dim]A Cyberpunk Terminal RPG[/dim]", justify="center")
    console.print()
    time.sleep(1)

    # Player stats
    minutes = int(state.play_time_minutes())
    console.print("[dim]── YOUR SESSION ──[/dim]", justify="center")
    console.print()
    console.print(f"[dim]Play time: {minutes} minutes[/dim]", justify="center")
    console.print(f"[dim]Commands used: {len(state.commands_used)}[/dim]", justify="center")
    console.print(f"[dim]Files discovered: {len(state.files_read)}[/dim]", justify="center")
    console.print(f"[dim]Hints used: {state.hints_used}[/dim]", justify="center")
    console.print()
    time.sleep(2)

    ending_labels = {
        "A": "THE WHISTLEBLOWER",
        "B": "THE SURVIVOR",
        "C": "THE FIRESTARTER",
    }
    if state.ending:
        label = ending_labels.get(state.ending, "UNKNOWN")
        console.print(f"[bold]Ending: {label}[/bold]", justify="center")
        console.print()
        time.sleep(1)

    console.print("[dim]── CREDITS ──[/dim]", justify="center")
    console.print()
    time.sleep(0.5)

    credits = [
        ("Story & Design", "NEON VOID Team"),
        ("Engine", "Custom Python Shell"),
        ("Built With", "prompt_toolkit + Rich"),
        ("Inspired By", "Zork, Blade Runner, Mr. Robot"),
    ]

    for role, name in credits:
        console.print(f"[dim]{role}[/dim]", justify="center")
        console.print(f"[bold]{name}[/bold]", justify="center")
        console.print()
        time.sleep(0.8)

    time.sleep(1)
    console.print("[dim]── END OF EPISODE 1 ──[/dim]", justify="center")
    console.print()
    time.sleep(2)


def play_post_credits():
    """Play the post-credits sequel hook."""
    console.clear()
    time.sleep(2)

    # Terminal flickers back to life
    console.print("[dim]...[/dim]")
    time.sleep(1)
    console.print("[dim]......[/dim]")
    time.sleep(0.5)

    console.print()
    typewriter("> NEW MESSAGE FROM: UNKNOWN", min_delay=0.04, max_delay=0.08)
    time.sleep(0.5)
    typewriter('> SUBJECT: "You\'re not the first."', min_delay=0.04, max_delay=0.08)
    time.sleep(0.5)
    console.print()

    lines = [
        "There are others like you.",
        "Other facilities. Other subjects.",
        "Omnicron is just one head of the hydra.",
        "",
        "Find us.",
        "",
        "    /dev/null/ZERO",
    ]
    for line in lines:
        typewriter(f"> {line}" if line else ">", min_delay=0.03, max_delay=0.07)
        time.sleep(0.3)

    console.print()
    time.sleep(1)
    typewriter("> [CONNECTION TERMINATED]", min_delay=0.05, max_delay=0.1)
    time.sleep(3)

    console.print()
    console.print("[bold cyan]NEON VOID will return.[/bold cyan]", justify="center")
    console.print()
    time.sleep(2)
