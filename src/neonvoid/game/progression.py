"""Act progression and content gating logic."""

from __future__ import annotations

from neonvoid.game.state import GameState


def check_act_progression(state: GameState) -> int | None:
    """Check if the player should advance to a new act.

    Returns the new act number, or None if no change.
    """
    if state.act == 1 and state.connected_nexus_core:
        return 2
    if state.act == 2 and state.connected_archive:
        return 3
    if state.act == 3 and state.connected_lab9:
        return 4
    return None


def should_unlock_escape(state: GameState) -> bool:
    """Check if the escape directory should be created in lab-9."""
    return (
        state.act == 4
        and state.read_own_surveillance
        and state.found_schedule
        and not state.escape_unlocked
    )


def can_ssh_to(server: str, state: GameState) -> bool:
    """Check if the player can SSH to a given server."""
    requirements = {
        "nexus-core": state.found_ssh_creds,
        "archive": state.bypassed_firewall,
        "lab-9": state.found_backdoor,
    }
    return requirements.get(server, False)


def get_act_intro_text(act: int) -> str:
    """Get the narrative text for entering a new act."""
    intros = {
        2: (
            "[bold cyan]═══ ACT 2: WHAT HAPPENED? ═══[/bold cyan]\n\n"
            "You are inside the corporate mainframe. Every file here is a thread\n"
            "in a web of lies. Someone died to bring you this access.\n"
            "Find out what they knew -- and what it cost them."
        ),
        3: (
            "[bold yellow]═══ ACT 3: WHAT AM I? ═══[/bold yellow]\n\n"
            "The archive. Where secrets go to be buried.\n"
            "River Chen said the proof was here. The truth about Project LETHE.\n"
            "The truth about you.\n\n"
            "[dim]WARNING: All access to this server is being logged.[/dim]"
        ),
        4: (
            "[bold red]═══ ACT 4: ESCAPE ═══[/bold red]\n\n"
            "You are inside the system that controls the very room you sit in.\n"
            "The lab where minds are erased. Where YOUR mind was erased.\n"
            "The clock is ticking. Find the way out.\n\n"
            "[bold red]Or lose everything. Again.[/bold red]"
        ),
    }
    return intros.get(act, "")


def get_completion_percentage(state: GameState) -> float:
    """Calculate rough completion percentage."""
    total_flags = 0
    set_flags = 0

    key_flags = [
        "read_readme", "found_identity", "found_deleted_mail", "found_ssh_creds",
        "read_lethe_summary", "connected_nexus_core", "discovered_river_death",
        "read_chat_logs", "found_financial_evidence", "bypassed_firewall",
        "connected_archive", "extracted_evidence", "discovered_subject_031",
        "discovered_true_identity", "found_backdoor", "connected_lab9",
        "read_own_surveillance", "found_schedule", "unlocked_door", "escaped",
    ]

    for flag in key_flags:
        total_flags += 1
        if state.get_flag(flag):
            set_flags += 1

    return (set_flags / total_flags * 100) if total_flags > 0 else 0
