"""Visual effects: boot sequence, glitch, typewriter, connection animation."""

from __future__ import annotations

import random
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text

from neonvoid.ui.terminal import console


GLITCH_CHARS = "█▓▒░╔╗╚╝║═╠╣╬▄▀▐▌◄►"


def typewriter(text: str, min_delay: float = 0.01, max_delay: float = 0.04, newline: bool = True):
    """Print text character by character with random delays."""
    for char in text:
        console.print(char, end="", highlight=False)
        if char == "\n":
            time.sleep(min_delay * 2)
        elif char in ".!?":
            time.sleep(max_delay * 3)
        elif char == ",":
            time.sleep(max_delay * 1.5)
        else:
            time.sleep(random.uniform(min_delay, max_delay))
    if newline:
        console.print()


def typewriter_styled(text: str, style: str = "", delay: float = 0.02):
    """Typewriter effect with Rich styling applied to whole text."""
    for i, char in enumerate(text):
        console.print(f"[{style}]{char}[/{style}]" if style else char, end="", highlight=False)
        if char in ".!?":
            time.sleep(delay * 3)
        elif char == "\n":
            time.sleep(delay * 2)
        else:
            time.sleep(delay)
    console.print()


def glitch_text(text: str, intensity: float = 0.3, duration: float = 0.5):
    """Display text with a brief glitch effect."""
    iterations = int(duration / 0.05)
    for i in range(iterations):
        glitched = ""
        glitch_amount = intensity * (1 - i / iterations)  # Fade out
        for char in text:
            if random.random() < glitch_amount and char not in (" ", "\n"):
                glitched += random.choice(GLITCH_CHARS)
            else:
                glitched += char
        console.print(f"\r[bold cyan]{glitched}[/bold cyan]", end="")
        time.sleep(0.05)
    console.print(f"\r[bold cyan]{text}[/bold cyan]")


def boot_sequence():
    """Play the full boot sequence animation."""
    console.clear()
    time.sleep(0.5)

    # BIOS POST
    bios_lines = [
        "[dim]NEXUS BIOS v4.2.1[/dim]",
        "[dim]Omnicron Industries Secure Terminal[/dim]",
        "[dim]Serial: NX7-0031-CLASSIFIED[/dim]",
        "",
        "[dim]CPU: OmniCore X9 @ 4.7GHz ........ [green]OK[/green][/dim]",
        "[dim]RAM: 128GB DDR6 ................... [green]OK[/green][/dim]",
        "[dim]STORAGE: 2TB NVMe ................. [green]OK[/green][/dim]",
        "[dim]NETWORK: 10GbE Internal ........... [green]OK[/green][/dim]",
        "[dim]SECURITY MODULE: OmniShield v7 .... [green]OK[/green][/dim]",
        "",
    ]

    for line in bios_lines:
        console.print(line)
        time.sleep(0.15)

    time.sleep(0.3)

    # Memory check with glitch
    console.print("[dim]Running memory integrity check...[/dim]")
    time.sleep(0.5)
    console.print("[bold red]WARNING: MEMORY INTEGRITY CHECK FAILED[/bold red]")
    console.print("[bold red]WARNING: 7 SECTORS CORRUPTED[/bold red]")
    console.print("[bold yellow]WARNING: UNAUTHORIZED ACCESS PATTERN DETECTED[/bold yellow]")
    time.sleep(0.8)

    console.print()
    console.print("[dim]Loading NEXUS-OS kernel...[/dim]")

    # Progress bar for kernel loading
    with Progress(
        TextColumn("[dim]{task.description}[/dim]"),
        BarColumn(bar_width=40, complete_style="cyan", finished_style="green"),
        TextColumn("[dim]{task.percentage:>3.0f}%[/dim]"),
        console=console,
    ) as progress:
        task = progress.add_task("Kernel modules", total=100)
        for i in range(100):
            progress.update(task, advance=1)
            delay = 0.01
            # Stutter at certain points
            if i in (23, 47, 71, 89):
                delay = 0.3
            time.sleep(delay)

    console.print()
    time.sleep(0.3)

    # System identification
    lines = [
        "[bold cyan]╔══════════════════════════════════════════════════════╗[/bold cyan]",
        "[bold cyan]║                                                      ║[/bold cyan]",
        "[bold cyan]║     N E X U S - 7   T E R M I N A L   v 4.2.1      ║[/bold cyan]",
        "[bold cyan]║                                                      ║[/bold cyan]",
        "[bold cyan]║     OMNICRON INDUSTRIES - INTERNAL USE ONLY          ║[/bold cyan]",
        "[bold cyan]║     CLASSIFICATION: RESTRICTED                       ║[/bold cyan]",
        "[bold cyan]║                                                      ║[/bold cyan]",
        "[bold cyan]╚══════════════════════════════════════════════════════╝[/bold cyan]",
    ]
    for line in lines:
        console.print(line)
        time.sleep(0.08)

    time.sleep(0.5)
    console.print()
    console.print("[dim]> ENTERING RECOVERY MODE...[/dim]")
    time.sleep(0.3)
    console.print("[dim]> USER SESSION RESTORED: [bold]VOSS, K.[/bold][/dim]")
    time.sleep(0.3)
    console.print("[dim]> LAST LOGIN: [bold red]█▓▒░CORRUPTED░▒▓█[/bold red][/dim]")
    time.sleep(0.5)
    console.print()

    # Tutorial hint
    console.print(Panel(
        "[dim]Terminal recovery complete. System integrity compromised.\n"
        "Type [bold]ls[/bold] to view files. Type [bold]help[/bold] for available commands.\n"
        "Type [bold]hint[/bold] if you get stuck.[/dim]",
        border_style="dim yellow",
        title="[yellow]SYSTEM NOTICE[/yellow]",
        padding=(1, 2),
    ))
    console.print()


def ssh_connection_animation(server: str, user: str):
    """Play SSH connection animation."""
    console.print()
    console.print(f"[dim]Connecting to {server}...[/dim]")
    time.sleep(0.3)

    # Fake routing
    hops = [
        f"[dim]  hop 1: 10.0.0.1 (gateway) ........ {random.randint(1, 5)}ms[/dim]",
        f"[dim]  hop 2: 10.0.7.254 (switch-7) ...... {random.randint(1, 3)}ms[/dim]",
    ]
    if server == "archive":
        hops.append(f"[dim]  hop 3: 10.0.7.100 (firewall) ..... {random.randint(2, 8)}ms[/dim]")
    if server == "lab-9":
        hops.append(f"[dim]  hop 3: 10.0.9.254 (tunnel) ....... {random.randint(5, 15)}ms[/dim]")
        hops.append(f"[dim]  hop 4: 10.0.9.1 (lab-9) ......... {random.randint(2, 5)}ms[/dim]")

    for hop in hops:
        console.print(hop)
        time.sleep(0.2)

    time.sleep(0.3)
    console.print(f"[dim]  Authenticating {user}@{server}...[/dim]")
    time.sleep(0.4)
    console.print(f"[green]  Connected.[/green]")
    console.print()

    # Server banner
    banners = {
        "nexus-core": (
            "[cyan]╔═══════════════════════════════════╗\n"
            "║  NEXUS-CORE CORPORATE SERVER      ║\n"
            "║  Omnicron Industries Mainframe     ║\n"
            "║  Authorized Personnel Only         ║\n"
            "╚═══════════════════════════════════╝[/cyan]"
        ),
        "archive": (
            "[yellow]╔═══════════════════════════════════╗\n"
            "║  ARCHIVE DEEP STORAGE             ║\n"
            "║  Classification: TOP SECRET       ║\n"
            "║  All Access Logged & Monitored    ║\n"
            "╚═══════════════════════════════════╝[/yellow]"
        ),
        "lab-9": (
            "[red]╔═══════════════════════════════════╗\n"
            "║  LAB-9 RESEARCH FACILITY          ║\n"
            "║  PROJECT LETHE - ACTIVE           ║\n"
            "║  ⚠  BIOHAZARD LEVEL 3  ⚠         ║\n"
            "╚═══════════════════════════════════╝[/red]"
        ),
    }

    if server in banners:
        console.print(banners[server])
        console.print()


def ssh_disconnect_animation(server: str):
    """Play SSH disconnect animation."""
    console.print(f"\n[dim]Connection to {server} closed.[/dim]")
    time.sleep(0.3)
    console.print("[dim]Returning to local terminal...[/dim]\n")
    time.sleep(0.2)


def discovery_effect(text: str):
    """A dramatic reveal effect for major discoveries."""
    console.print()
    console.print("[dim]" + "─" * 60 + "[/dim]")
    time.sleep(0.3)

    # Glitch before reveal
    for _ in range(3):
        glitch_line = "".join(random.choice(GLITCH_CHARS) for _ in range(60))
        console.print(f"[dim red]{glitch_line}[/dim red]", end="\r")
        time.sleep(0.1)

    console.print(" " * 60, end="\r")
    time.sleep(0.2)

    typewriter_styled(text, style="bold yellow")

    console.print("[dim]" + "─" * 60 + "[/dim]")
    console.print()


def ending_sequence(ending: str, text: str):
    """Play an ending sequence with dramatic effects."""
    console.clear()
    time.sleep(1)

    # Static effect
    for _ in range(5):
        static = "".join(random.choice(GLITCH_CHARS + " " * 10) for _ in range(60))
        console.print(f"[dim]{static}[/dim]")
        time.sleep(0.05)

    console.print()
    time.sleep(0.5)

    # Ending text with typewriter
    for paragraph in text.split("\n\n"):
        typewriter(paragraph, min_delay=0.02, max_delay=0.05)
        console.print()
        time.sleep(1)

    time.sleep(2)
