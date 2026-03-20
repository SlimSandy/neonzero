"""Event/trigger system - maps player actions to narrative beats and state changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from neonvoid.game.state import GameState


@dataclass
class Trigger:
    """A trigger that fires when conditions are met."""
    name: str
    condition: Callable[[GameState, str, list[str], str], bool]
    flags_to_set: list[str] = field(default_factory=list)
    narrative_key: str | None = None
    once: bool = True
    _fired: bool = False

    def check(self, state: GameState, cmd: str, args: list[str], output: str) -> bool:
        """Check if this trigger should fire."""
        if self.once and self._fired:
            return False
        if self.condition(state, cmd, args, output):
            self._fired = True
            return True
        return False

    def apply(self, state: GameState):
        """Apply state changes from this trigger."""
        for flag in self.flags_to_set:
            state.set_flag(flag)


def _file_read(filepath_contains: str):
    """Create a condition that checks if a specific file was just read (case-insensitive)."""
    def check(state: GameState, cmd: str, args: list[str], output: str) -> bool:
        if cmd not in ("cat", "less", "more"):
            return False
        target = filepath_contains.lower()
        return any(target in arg.lower() for arg in args)
    return check


def _command_with_pattern(cmd_name: str, pattern: str):
    """Create a condition that checks for a command with a specific pattern in args."""
    def check(state: GameState, cmd: str, args: list[str], output: str) -> bool:
        if cmd != cmd_name:
            return False
        return any(pattern.lower() in arg.lower() for arg in args)
    return check


def _entered_directory(dir_name: str):
    """Create a condition that checks if player cd'd into a directory (case-insensitive)."""
    def check(state: GameState, cmd: str, args: list[str], output: str) -> bool:
        if cmd != "cd":
            return False
        target = dir_name.lower()
        return any(target in arg.lower() for arg in args)
    return check


def _chmod_file(filename: str):
    """Create a condition for chmod on a specific file."""
    def check(state: GameState, cmd: str, args: list[str], output: str) -> bool:
        if cmd != "chmod":
            return False
        return any(filename in arg for arg in args) and output == ""
    return check


def _grep_pattern(pattern: str):
    """Create a condition for grepping a specific pattern."""
    def check(state: GameState, cmd: str, args: list[str], output: str) -> bool:
        if cmd != "grep":
            return False
        return any(pattern.lower() in arg.lower() for arg in args)
    return check


def _tar_extract(filename: str):
    """Create a condition for extracting a specific archive."""
    def check(state: GameState, cmd: str, args: list[str], output: str) -> bool:
        if cmd != "tar":
            return False
        return any(filename in arg for arg in args) and "Extracted" in output
    return check


def _ssh_connected(server: str):
    """Create a condition for SSH connecting to a server."""
    def check(state: GameState, cmd: str, args: list[str], output: str) -> bool:
        if cmd != "ssh":
            return False
        return f"__SSH_CONNECT__{server}" in output
    return check


def build_triggers() -> list[Trigger]:
    """Build all game triggers."""
    return [
        # ═══════════════════════════════════
        # ACT 1: "WHO AM I?"
        # ═══════════════════════════════════

        Trigger(
            name="read_readme",
            condition=_file_read("README.txt"),
            flags_to_set=["read_readme"],
            narrative_key="act1_readme",
        ),

        Trigger(
            name="found_identity",
            condition=_file_read("001_welcome.msg"),
            flags_to_set=["found_identity"],
            narrative_key="act1_identity",
        ),

        Trigger(
            name="read_urgent",
            condition=_file_read("003_urgent.msg"),
            flags_to_set=["read_urgent_email"],
            narrative_key="act1_urgent",
        ),

        Trigger(
            name="found_deleted_mail",
            condition=_entered_directory(".deleted"),
            flags_to_set=["found_deleted_mail"],
            narrative_key="act1_deleted_mail",
        ),

        Trigger(
            name="found_ssh_creds",
            condition=_file_read("005_coordinates.msg"),
            flags_to_set=["found_ssh_creds"],
            narrative_key="act1_ssh_creds",
        ),

        Trigger(
            name="grepped_lethe",
            condition=_grep_pattern("lethe"),
            flags_to_set=["grepped_lethe"],
            narrative_key="act1_grep_lethe",
        ),

        Trigger(
            name="unlocked_lethe_summary",
            condition=_chmod_file("project_lethe_summary"),
            flags_to_set=["unlocked_lethe_summary"],
            narrative_key="act1_chmod_lethe",
        ),

        Trigger(
            name="read_lethe_summary",
            condition=_file_read("project_lethe_summary"),
            flags_to_set=["read_lethe_summary"],
            narrative_key="act1_lethe_revealed",
        ),

        Trigger(
            name="mapped_network",
            condition=_file_read("hosts"),
            flags_to_set=["mapped_network"],
            narrative_key="act1_network",
        ),

        # ═══════════════════════════════════
        # ACT 2: "WHAT HAPPENED?"
        # ═══════════════════════════════════

        Trigger(
            name="connected_nexus_core",
            condition=_ssh_connected("nexus-core"),
            flags_to_set=["connected_nexus_core"],
            narrative_key="act2_enter",
        ),

        Trigger(
            name="discovered_river_death",
            condition=_file_read("chen_river.record"),
            flags_to_set=["discovered_river_death"],
            narrative_key="act2_river_death",
        ),

        Trigger(
            name="read_chat_logs",
            condition=_file_read("project_lethe.log"),
            flags_to_set=["read_chat_logs"],
            narrative_key="act2_chat_logs",
        ),

        Trigger(
            name="read_private_messages",
            condition=_file_read("chen_voss.log"),
            flags_to_set=["read_private_messages"],
            narrative_key="act2_private_msg",
        ),

        Trigger(
            name="found_financial_evidence",
            condition=_file_read("offshore_transfers.log"),
            flags_to_set=["found_financial_evidence"],
            narrative_key="act2_financial",
        ),

        Trigger(
            name="reviewed_camera_logs",
            condition=_file_read("lab_9.log"),
            flags_to_set=["reviewed_camera_logs"],
            narrative_key="act2_cameras",
        ),

        Trigger(
            name="heard_voicemail",
            condition=_file_read("vm_002.txt"),
            flags_to_set=["heard_voicemail"],
            narrative_key="act2_voicemail",
        ),

        Trigger(
            name="read_firewall_rules",
            condition=_file_read("rules.conf"),
            flags_to_set=["read_firewall_rules"],
            narrative_key="act2_firewall_hint",
        ),

        # ═══════════════════════════════════
        # ACT 3: "WHAT AM I?"
        # ═══════════════════════════════════

        Trigger(
            name="connected_archive",
            condition=_ssh_connected("archive"),
            flags_to_set=["connected_archive"],
            narrative_key="act3_enter",
        ),

        Trigger(
            name="found_evidence_archive",
            condition=_file_read("EVIDENCE.tar.gz"),
            flags_to_set=["found_evidence_archive"],
            narrative_key=None,  # tar.gz can't be cat'd, but finding it matters
        ),

        Trigger(
            name="extracted_evidence",
            condition=_tar_extract("EVIDENCE"),
            flags_to_set=["extracted_evidence"],
            narrative_key="act3_evidence_extracted",
        ),

        Trigger(
            name="discovered_subject_031",
            condition=_file_read("subject_031.txt"),
            flags_to_set=["discovered_subject_031"],
            narrative_key="act3_subject_031",
        ),

        Trigger(
            name="discovered_true_identity",
            condition=_file_read("voss_kai_ORIGINAL.record"),
            flags_to_set=["discovered_true_identity"],
            narrative_key="act3_true_identity",
        ),

        Trigger(
            name="found_backdoor",
            condition=_file_read("README_RIVER.txt"),
            flags_to_set=["found_backdoor"],
            narrative_key="act3_backdoor",
        ),

        Trigger(
            name="read_river_farewell",
            condition=_file_read("insurance.msg"),
            flags_to_set=["read_river_farewell"],
            narrative_key="act3_river_farewell",
        ),

        # ═══════════════════════════════════
        # ACT 4: "HOW DO I GET OUT?"
        # ═══════════════════════════════════

        Trigger(
            name="connected_lab9",
            condition=_ssh_connected("lab-9"),
            flags_to_set=["connected_lab9"],
            narrative_key="act4_enter",
        ),

        Trigger(
            name="read_own_surveillance",
            condition=_file_read("camera_feed.log"),
            flags_to_set=["read_own_surveillance"],
            narrative_key="act4_surveillance",
        ),

        Trigger(
            name="found_schedule",
            condition=_file_read("schedule.txt"),
            flags_to_set=["found_schedule"],
            narrative_key="act4_schedule",
        ),
    ]
