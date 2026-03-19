"""Puzzle validation and unlock mechanics."""

from __future__ import annotations

from neonvoid.game.state import GameState


# The passphrase components (assembled from clues throughout the game)
# LETHE = project name (from docs)
# 031 = player's subject number (from subject file)
# RC4471 = River Chen's employee ID (from her record)
# REMEMBER = keyword from River's farewell note
PASSPHRASE = "LETHE-031-RC4471-REMEMBER"
PASSPHRASE_LOWER = PASSPHRASE.lower()


def validate_passphrase(attempt: str) -> bool:
    """Check if the passphrase attempt is correct."""
    cleaned = attempt.strip().strip('"').strip("'")
    return cleaned == PASSPHRASE or cleaned.lower() == PASSPHRASE_LOWER


def check_firewall_bypass(args: list[str], state: GameState) -> tuple[bool, str]:
    """Handle the firewall-ctl command for the firewall bypass puzzle.

    The player needs to run: firewall-ctl disable-rule BLOCK_ARCHIVE
    """
    if len(args) < 2:
        return False, (
            "Usage: firewall-ctl <action> <rule_id>\n"
            "Actions: list-rules, disable-rule, enable-rule\n"
            "Use 'list-rules' to view active firewall rules."
        )

    action = args[0]
    rule_id = args[1] if len(args) > 1 else ""

    if action == "list-rules":
        return False, (
            "[dim]Active Firewall Rules:[/dim]\n"
            "  RULE_001  ALLOW  10.0.7.0/24  ->  nexus-core:22    [green]ACTIVE[/green]\n"
            "  RULE_002  ALLOW  10.0.7.0/24  ->  nexus-core:80    [green]ACTIVE[/green]\n"
            "  RULE_003  [bold red]DENY[/bold red]   ALL           ->  archive:*       [bold red]ACTIVE[/bold red]  # BLOCK_ARCHIVE\n"
            "  RULE_004  ALLOW  10.0.9.0/24  ->  lab-9:22         [green]ACTIVE[/green]\n"
            "\n[dim]Use 'firewall-ctl disable-rule <RULE_ID>' to disable a rule.[/dim]"
        )

    if action == "disable-rule":
        if rule_id in ("RULE_003", "BLOCK_ARCHIVE"):
            state.set_flag("bypassed_firewall")
            return True, (
                "[green]Rule RULE_003 (BLOCK_ARCHIVE) disabled.[/green]\n"
                "[dim]Archive server is now reachable.[/dim]"
            )
        elif rule_id in ("RULE_001", "RULE_002", "RULE_004"):
            return False, f"[yellow]Warning: Disabling {rule_id} would lock you out. Aborted.[/yellow]"
        else:
            return False, f"firewall-ctl: unknown rule '{rule_id}'"

    if action == "enable-rule":
        return False, f"firewall-ctl: rule '{rule_id}' is already active"

    return False, f"firewall-ctl: unknown action '{action}'"


def check_door_override(args: list[str], state: GameState) -> tuple[bool, str]:
    """Handle the door override script execution.

    Player runs: ./override.sh <passphrase>
    """
    if not args:
        return False, (
            "[dim]DOOR CONTROL SYSTEM v2.1[/dim]\n"
            "Usage: ./override.sh <passphrase>\n"
            "\n"
            "[yellow]PASSPHRASE HINT:[/yellow]\n"
            "[dim]The truth is scattered across the systems you have traversed.\n"
            "Combine what you know:\n"
            "  - The project that stole your mind\n"
            "  - Your designation within it\n"
            "  - The ID of the one who tried to save you\n"
            "  - What she told you never to do\n"
            "\n"
            "Format: WORD-NUMBER-ID-WORD[/dim]"
        )

    attempt = args[0] if args else ""

    if validate_passphrase(attempt):
        state.set_flag("unlocked_door")
        return True, ""  # Shell handles the dramatic reveal
    else:
        return False, (
            "[bold red]ACCESS DENIED[/bold red]\n"
            f"[dim]Passphrase '{attempt}' is incorrect.\n"
            "Re-examine the evidence. The answer is there.[/dim]"
        )
