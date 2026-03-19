"""Game state management - flags, persistence, save/load."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GameState:
    """Tracks all game progress, flags, and metadata."""

    act: int = 1
    current_server: str = "local"  # local | nexus-core | archive | lab-9
    files_read: list[str] = field(default_factory=list)
    commands_used: set[str] = field(default_factory=set)
    hints_used: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    ending: str | None = None  # A | B | C
    last_command_time: float = field(default_factory=time.time)

    # -- Act 1 flags --
    read_readme: bool = False
    found_identity: bool = False
    found_deleted_mail: bool = False
    found_ssh_creds: bool = False
    unlocked_lethe_summary: bool = False
    read_lethe_summary: bool = False
    mapped_network: bool = False
    read_urgent_email: bool = False
    grepped_lethe: bool = False

    # -- Act 2 flags --
    connected_nexus_core: bool = False
    discovered_river_death: bool = False
    read_chat_logs: bool = False
    read_private_messages: bool = False
    found_financial_evidence: bool = False
    reviewed_camera_logs: bool = False
    heard_voicemail: bool = False
    bypassed_firewall: bool = False

    # -- Act 3 flags --
    connected_archive: bool = False
    found_evidence_archive: bool = False
    extracted_evidence: bool = False
    discovered_subject_031: bool = False
    discovered_true_identity: bool = False
    found_backdoor: bool = False
    read_river_farewell: bool = False

    # -- Act 4 flags --
    connected_lab9: bool = False
    read_own_surveillance: bool = False
    found_schedule: bool = False
    escape_unlocked: bool = False
    assembled_passphrase: bool = False
    unlocked_door: bool = False
    sent_evidence: bool = False
    sent_evidence_all: bool = False
    escaped: bool = False

    def set_flag(self, flag_name: str, value: bool = True) -> bool:
        """Set a flag and return True if it changed."""
        if not hasattr(self, flag_name):
            return False
        old = getattr(self, flag_name)
        if old == value:
            return False
        setattr(self, flag_name, value)
        return True

    def get_flag(self, flag_name: str) -> bool:
        """Get a flag value, defaulting to False."""
        return getattr(self, flag_name, False)

    def record_file_read(self, filepath: str) -> bool:
        """Record a file being read. Returns True if it's the first time."""
        if filepath not in self.files_read:
            self.files_read.append(filepath)
            return True
        return False

    def record_command(self, command_name: str):
        """Record a command being used."""
        self.commands_used.add(command_name)
        self.last_command_time = time.time()

    def time_since_last_command(self) -> float:
        """Seconds since the last command was entered."""
        return time.time() - self.last_command_time

    def play_time_minutes(self) -> float:
        """Total play time in minutes."""
        end = self.end_time or time.time()
        return (end - self.start_time) / 60

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a saveable dict."""
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, set):
                d[k] = list(v)
            else:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameState:
        """Deserialize from a saved dict."""
        state = cls.__new__(cls)
        for k, v in data.items():
            if k == "commands_used":
                setattr(state, k, set(v) if isinstance(v, list) else v)
            else:
                setattr(state, k, v)
        return state

    def save(self, path: Path):
        """Save state to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> GameState | None:
        """Load state from a JSON file. Returns None if not found."""
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            return cls.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None
