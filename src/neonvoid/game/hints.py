"""State-aware hint system with multi-step objectives and 5 escalation tiers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from neonvoid.game.state import GameState


# ═══════════════════════════════════════════════════════════
# HINT STEP: one actionable step within an objective
# ═══════════════════════════════════════════════════════════

@dataclass
class HintStep:
    """A single actionable step within a multi-step objective."""
    action: str           # Short description: "Read the firewall rules"
    nudge: str            # Tier 1 - atmospheric/thematic
    hint: str             # Tier 2 - names the command or location
    walkthrough: str      # Tier 3 - exact command to type
    done_when: Callable[[GameState], bool]  # Predicate: is this step complete?


# ═══════════════════════════════════════════════════════════
# HELPERS for done_when predicates
# ═══════════════════════════════════════════════════════════

def _has_read(state: GameState, filename_part: str) -> bool:
    """Check if the player has read a file containing filename_part (case-insensitive)."""
    target = filename_part.lower()
    return any(target in f.lower() for f in state.files_read)


def _has_cmd(state: GameState, cmd: str) -> bool:
    """Check if the player has used a command."""
    return cmd in state.commands_used


class HintSystem:
    """Provides contextual, state-aware hints based on current game progress."""

    def __init__(self):
        self._hint_counts: dict[str, int] = {}

    def get_hint(self, state: GameState) -> str:
        """Get a hint appropriate to the player's current progress."""
        state.hints_used += 1

        # Determine current objective
        hint_key = self._get_current_objective(state)
        steps = HINTS.get(hint_key, [])
        objective = OBJECTIVES.get(hint_key, "Explore and investigate.")

        if not steps:
            return "[dim cyan]No hint available. Try exploring with [bold]ls[/bold] and [bold]cat[/bold].[/dim cyan]"

        # Find the first incomplete step
        step_idx, active_step = self._find_active_step(steps, state)

        if active_step is None:
            # All steps done but objective flag not yet set — safety fallback
            return (
                "[bold green]You've completed all the steps for this objective.[/bold green]\n"
                "[dim]The game should advance shortly. Try running a command or exploring.[/dim]"
            )

        # Per-step tier counter (resets when step advances)
        step_key = f"{hint_key}:{step_idx}"
        self._hint_counts[step_key] = self._hint_counts.get(step_key, 0) + 1
        tier = min(self._hint_counts[step_key], 5)

        # Build the hint text based on tier
        if tier == 1:
            hint_text = active_step.nudge
        elif tier == 2:
            hint_text = active_step.hint
        elif tier == 3:
            hint_text = active_step.walkthrough
        elif tier == 4:
            hint_text = self._build_solution(active_step)
        else:  # tier 5+
            hint_text = self._build_lifeline(steps, step_idx, state)

        # Visual styling per tier
        tier_styles = {
            1: ("NUDGE", "dim cyan", "░"),
            2: ("HINT", "cyan", "▒"),
            3: ("WALKTHROUGH", "bold yellow", "█"),
            4: ("SOLUTION", "bold magenta", "▓"),
            5: ("LIFELINE", "bold red", "█"),
        }
        label, style, block = tier_styles.get(tier, ("HINT", "cyan", "▒"))

        border = block * 50
        lines = [
            f"[{style}]{border}[/{style}]",
            f"[{style}]  {label} (tier {tier}/5)[/{style}]",
            f"[{style}]{border}[/{style}]",
            "",
            f"[dim]Current objective:[/dim] [bold]{objective}[/bold]",
            f"[dim]Current step:[/dim] {active_step.action}",
            "",
            hint_text,
            "",
        ]

        # Show completed steps for context
        if step_idx > 0:
            completed = []
            for i in range(step_idx):
                completed.append(f"  [green]✓[/green] [dim]{steps[i].action}[/dim]")
            lines.insert(7, "[dim]Already done:[/dim]")
            for i, c in enumerate(completed):
                lines.insert(8 + i, c)
            lines.insert(8 + len(completed), "")

        if tier < 5:
            lines.append(
                f"[dim]Type [bold]hint[/bold] again for a stronger hint "
                f"({tier + 1}/5).[/dim]"
            )
        else:
            lines.append(
                "[dim]This is the maximum hint. All remaining steps are listed above.[/dim]"
            )

        # Show progress context
        progress = self._get_progress_summary(state)
        if progress:
            lines.append("")
            lines.append(f"[dim]{progress}[/dim]")

        return "\n".join(lines)

    def _find_active_step(
        self, steps: list[HintStep], state: GameState
    ) -> tuple[int, HintStep | None]:
        """Find the first incomplete step. Returns (index, step) or (len, None)."""
        for i, step in enumerate(steps):
            if not step.done_when(state):
                return i, step
        return len(steps), None

    def _build_solution(self, step: HintStep) -> str:
        """Tier 4: Bold command repeat with explanation."""
        return (
            f"[bold]Type this exact command now:[/bold]\n"
            f"\n"
            f"  [bold green on black] {step.walkthrough.strip()} [/bold green on black]\n"
            f"\n"
            f"[dim]This will: {step.action.lower()}[/dim]"
        )

    def _build_lifeline(
        self, steps: list[HintStep], current_idx: int, state: GameState
    ) -> str:
        """Tier 5: Show all remaining steps as a numbered checklist."""
        lines = ["[bold]Complete walkthrough — all remaining steps:[/bold]\n"]
        num = 1
        for i in range(current_idx, len(steps)):
            step = steps[i]
            if step.done_when(state):
                continue
            lines.append(f"  [bold yellow]{num}.[/bold yellow] {step.action}")
            lines.append(f"     [bold green]{step.walkthrough.strip()}[/bold green]")
            lines.append("")
            num += 1
        lines.append("[dim]Follow these steps in order to complete this objective.[/dim]")
        return "\n".join(lines)

    def _get_current_objective(self, state: GameState) -> str:
        """Determine what the player should be working on."""
        # Act 1
        if state.act == 1:
            if not state.read_readme:
                return "explore_start"
            if not state.found_identity:
                return "find_identity"
            if not state.read_urgent_email:
                return "read_emails"
            if not state.found_deleted_mail:
                return "find_deleted"
            if not state.found_ssh_creds:
                return "find_ssh_creds"
            if not state.grepped_lethe:
                return "search_lethe"
            if not state.unlocked_lethe_summary:
                return "unlock_lethe"
            if not state.read_lethe_summary:
                return "read_lethe"
            if not state.mapped_network:
                return "map_network"
            return "ssh_nexus"

        # Act 2
        if state.act == 2:
            if not state.discovered_river_death:
                return "investigate_river"
            if not state.read_chat_logs:
                return "read_chats"
            if not state.found_financial_evidence:
                return "find_finances"
            if not state.reviewed_camera_logs:
                return "check_cameras"
            if not state.heard_voicemail:
                return "check_voicemail"
            if not state.bypassed_firewall:
                return "bypass_firewall"
            return "ssh_archive"

        # Act 3
        if state.act == 3:
            if not state.extracted_evidence:
                return "find_evidence"
            if not state.discovered_subject_031:
                return "read_subjects"
            if not state.discovered_true_identity:
                return "find_true_identity"
            if not state.found_backdoor:
                return "find_backdoor"
            return "ssh_lab9"

        # Act 4
        if state.act == 4:
            if not state.read_own_surveillance:
                return "read_surveillance"
            if not state.found_schedule:
                return "find_schedule"
            if not state.escape_unlocked:
                return "wait_escape_unlock"
            if not state.unlocked_door:
                return "solve_passphrase"
            return "make_choice"

        return "explore_start"

    def _get_progress_summary(self, state: GameState) -> str:
        """Show a brief summary of where the player stands."""
        act_names = {1: "Who Am I?", 2: "What Happened?", 3: "What Am I?", 4: "Escape"}
        act_name = act_names.get(state.act, "???")

        act1_done = sum([
            state.read_readme, state.found_identity, state.read_urgent_email,
            state.found_deleted_mail, state.found_ssh_creds, state.grepped_lethe,
            state.unlocked_lethe_summary, state.read_lethe_summary,
            state.mapped_network,
        ])
        act2_done = sum([
            state.discovered_river_death, state.read_chat_logs,
            state.found_financial_evidence, state.reviewed_camera_logs,
            state.heard_voicemail, state.bypassed_firewall,
        ])
        act3_done = sum([
            state.extracted_evidence, state.discovered_subject_031,
            state.discovered_true_identity, state.found_backdoor,
        ])
        act4_done = sum([
            state.read_own_surveillance, state.found_schedule,
            state.escape_unlocked, state.unlocked_door,
        ])

        progress_map = {
            1: f"Act 1 progress: {act1_done}/9 objectives",
            2: f"Act 2 progress: {act2_done}/6 objectives",
            3: f"Act 3 progress: {act3_done}/4 objectives",
            4: f"Act 4 progress: {act4_done}/4 objectives",
        }

        return f"[Act {state.act}: {act_name}] {progress_map.get(state.act, '')}"


# ═══════════════════════════════════════════════════════════
# OBJECTIVE DESCRIPTIONS (shown as "Current objective:")
# ═══════════════════════════════════════════════════════════

OBJECTIVES: dict[str, str] = {
    # Act 1
    "explore_start": "Figure out where you are",
    "find_identity": "Discover your identity",
    "read_emails": "Read all your messages",
    "find_deleted": "Find what was hidden from you",
    "find_ssh_creds": "Find network access credentials",
    "search_lethe": "Investigate Project LETHE",
    "unlock_lethe": "Access the locked LETHE document",
    "read_lethe": "Read the LETHE summary",
    "map_network": "Map the network to find other servers",
    "ssh_nexus": "Connect to the corporate server",
    # Act 2
    "investigate_river": "Find out who 'R' is",
    "read_chats": "Read the internal communications",
    "find_finances": "Follow the money trail",
    "check_cameras": "Review security camera footage",
    "check_voicemail": "Check your voicemail",
    "bypass_firewall": "Disable the archive firewall block",
    "ssh_archive": "Connect to the archive server",
    # Act 3
    "find_evidence": "Find and extract River's evidence archive",
    "read_subjects": "Read the LETHE subject files",
    "find_true_identity": "Discover your original identity",
    "find_backdoor": "Find River's backdoor into Lab-9",
    "ssh_lab9": "Connect to Lab-9",
    # Act 4
    "read_surveillance": "Access the surveillance system",
    "find_schedule": "Find the procedure schedule",
    "wait_escape_unlock": "Trigger the escape route",
    "solve_passphrase": "Unlock the door to Room 31",
    "make_choice": "Decide what to do with the evidence",
}


# ═══════════════════════════════════════════════════════════
# HINTS: Ordered step lists per objective
#   Each HintStep has:
#     - action: what the player needs to do
#     - nudge (tier 1): atmospheric, points a direction
#     - hint (tier 2): names the command or location
#     - walkthrough (tier 3): exact command to type
#     - done_when: predicate checking if this step is complete
#   Tiers 4-5 are auto-generated from the step data.
# ═══════════════════════════════════════════════════════════

HINTS: dict[str, list[HintStep]] = {

    # ═══════════ ACT 1 ═══════════

    "explore_start": [
        HintStep(
            action="List files in the current directory",
            nudge=(
                "The cursor blinks. The terminal waits. What's around you?\n"
                "In a real terminal, you'd start by [italic]listing[/italic] what's here."
            ),
            hint=(
                "The command [bold cyan]ls[/bold cyan] lists files and directories.\n"
                "Try it. See what's on this machine."
            ),
            walkthrough="ls",
            done_when=lambda s: _has_cmd(s, "ls"),
        ),
        HintStep(
            action="Navigate to the desktop directory",
            nudge=(
                "You can see what's here now. One of these directories looks\n"
                "like a good starting point — where you'd normally find notes."
            ),
            hint=(
                "Use [bold cyan]cd desktop[/bold cyan] to enter the desktop directory.\n"
                "The [bold cyan]cd[/bold cyan] command changes your current directory."
            ),
            walkthrough="cd desktop",
            done_when=lambda s: _has_read(s, "README"),
        ),
        HintStep(
            action="Read the README file",
            nudge=(
                "There's a file here that someone left for you.\n"
                "It's practically screaming to be read."
            ),
            hint=(
                "Use [bold cyan]cat README.txt[/bold cyan] to read the contents\n"
                "of the README file."
            ),
            walkthrough="cat README.txt",
            done_when=lambda s: s.read_readme,
        ),
    ],

    "find_identity": [
        HintStep(
            action="Navigate to the mail inbox",
            nudge=(
                "The README said to check your mail. Someone left messages\n"
                "for you. Your identity might be in those messages."
            ),
            hint=(
                "Navigate to the [bold]mail/inbox[/bold] directory.\n"
                "Use [bold cyan]cd ~/mail/inbox[/bold cyan] to get there."
            ),
            walkthrough="cd ~/mail/inbox",
            done_when=lambda s: _has_read(s, "001_welcome") or _has_read(s, "inbox"),
        ),
        HintStep(
            action="Read the welcome email",
            nudge=(
                "There are messages waiting. Start with the first one —\n"
                "it should tell you who you are."
            ),
            hint=(
                "Read the messages with [bold cyan]cat[/bold cyan].\n"
                "Start with [bold]001_welcome.msg[/bold]."
            ),
            walkthrough="cat 001_welcome.msg",
            done_when=lambda s: s.found_identity,
        ),
    ],

    "read_emails": [
        HintStep(
            action="Read the urgent message",
            nudge=(
                "You've found some messages, but not all of them.\n"
                "Someone sent you something [italic]urgent[/italic]. Keep reading."
            ),
            hint=(
                "There are more messages in your inbox. Message 003\n"
                "has important information. Read it."
            ),
            walkthrough="cat 003_urgent.msg",
            done_when=lambda s: s.read_urgent_email,
        ),
    ],

    "find_deleted": [
        HintStep(
            action="Reveal hidden files in the mail directory",
            nudge=(
                "The urgent message told you to \"delete everything.\"\n"
                "But deletion is rarely permanent. What's hidden in\n"
                "plain sight? Some things are [italic]invisible[/italic] by default..."
            ),
            hint=(
                "In Linux, files starting with a dot (.) are hidden.\n"
                "The [bold cyan]ls -a[/bold cyan] command reveals them.\n"
                "Try it in the [bold]mail[/bold] directory."
            ),
            walkthrough="ls -a ~/mail",
            done_when=lambda s: s.found_deleted_mail,
        ),
        HintStep(
            action="Enter the hidden .deleted directory",
            nudge="You found something hidden. Go inside.",
            hint="Use [bold cyan]cd .deleted[/bold cyan] to enter the hidden folder.",
            walkthrough="cd ~/mail/.deleted",
            done_when=lambda s: s.found_deleted_mail,
        ),
    ],

    "find_ssh_creds": [
        HintStep(
            action="Read the deleted messages",
            nudge=(
                "The deleted messages contain something valuable.\n"
                "Read them all — one has the keys to the network."
            ),
            hint=(
                "There are two deleted messages. One has [bold]SSH credentials[/bold]\n"
                "to access another server. Read both."
            ),
            walkthrough="cat 005_coordinates.msg",
            done_when=lambda s: s.found_ssh_creds,
        ),
    ],

    "search_lethe": [
        HintStep(
            action="Search the logs for LETHE references",
            nudge=(
                "\"LETHE\" keeps appearing. What is it? The answer is\n"
                "buried in the system logs. You need to [italic]search[/italic] for it."
            ),
            hint=(
                "The [bold cyan]grep[/bold cyan] command searches inside files.\n"
                "Use it with [bold]-ri[/bold] to search recursively and case-insensitively\n"
                "through the logs directory."
            ),
            walkthrough="grep -ri \"lethe\" ~/logs/",
            done_when=lambda s: s.grepped_lethe,
        ),
    ],

    "unlock_lethe": [
        HintStep(
            action="Check file permissions in the docs directory",
            nudge=(
                "There's a document about Project LETHE in your docs\n"
                "folder, but it's locked down. Permissions are just\n"
                "numbers — and numbers can be changed."
            ),
            hint=(
                "Use [bold cyan]ls -l docs/[/bold cyan] to see file permissions.\n"
                "One file has no read permission (----------)."
            ),
            walkthrough="ls -l ~/docs/",
            done_when=lambda s: _has_read(s, "project_lethe_summary"),
        ),
        HintStep(
            action="Grant read permission to the locked file",
            nudge="You found the locked file. Now change its permissions.",
            hint=(
                "Use [bold cyan]chmod +r[/bold cyan] to add read permission.\n"
                "Target the LETHE summary file in docs/."
            ),
            walkthrough="chmod +r ~/docs/project_lethe_summary.txt",
            done_when=lambda s: s.unlocked_lethe_summary,
        ),
    ],

    "read_lethe": [
        HintStep(
            action="Read the LETHE summary document",
            nudge="You unlocked it. Now [italic]read[/italic] it. The truth about this place is in that file.",
            hint="Use [bold cyan]cat[/bold cyan] to read the LETHE summary you just unlocked.",
            walkthrough="cat ~/docs/project_lethe_summary.txt",
            done_when=lambda s: s.read_lethe_summary,
        ),
    ],

    "map_network": [
        HintStep(
            action="Read the network hosts file",
            nudge=(
                "You have SSH credentials from River, but you need to\n"
                "know where to connect. The network configuration files\n"
                "will show you the map."
            ),
            hint=(
                "Check the [bold]network/[/bold] directory for a hosts file.\n"
                "Also look at [bold].ssh/config[/bold] for SSH target details."
            ),
            walkthrough="cat ~/network/hosts",
            done_when=lambda s: s.mapped_network,
        ),
    ],

    "ssh_nexus": [
        HintStep(
            action="SSH to the corporate server",
            nudge=(
                "You have credentials. You know the server name. It's\n"
                "time to leave the local terminal and go deeper."
            ),
            hint=(
                "Use the [bold cyan]ssh[/bold cyan] command to connect.\n"
                "The format is [bold]ssh user@server[/bold]."
            ),
            walkthrough="ssh kai@nexus-core",
            done_when=lambda s: s.connected_nexus_core,
        ),
    ],

    # ═══════════ ACT 2 ═══════════

    "investigate_river": [
        HintStep(
            action="Find River Chen's employee record",
            nudge=(
                "\"R\" sent those emails. Who are they? A corporation this\n"
                "big keeps records on everyone. Find the HR department."
            ),
            hint=(
                "Navigate to [bold]hr/employees/[/bold] and look at the\n"
                "files there. Someone with the name 'chen' might be 'R'."
            ),
            walkthrough="cat hr/employees/chen_river.record",
            done_when=lambda s: s.discovered_river_death,
        ),
    ],

    "read_chats": [
        HintStep(
            action="Read the internal chat logs",
            nudge=(
                "People talk, and corporations log everything. Internal\n"
                "communications could reveal the dynamics behind what happened."
            ),
            hint=(
                "Check the [bold]comms/[/bold] directory. There are internal\n"
                "chat logs about Project LETHE."
            ),
            walkthrough="cat comms/internal_chat/project_lethe.log",
            done_when=lambda s: s.read_chat_logs,
        ),
    ],

    "find_finances": [
        HintStep(
            action="Find the financial evidence",
            nudge=(
                "Corruption leaves a paper trail. Follow the money\n"
                "and you'll find the motive."
            ),
            hint=(
                "The [bold]finance/[/bold] directory has transaction logs.\n"
                "Look for offshore transfers or unusual payments."
            ),
            walkthrough="cat finance/transactions/offshore_transfers.log",
            done_when=lambda s: s.found_financial_evidence,
        ),
    ],

    "check_cameras": [
        HintStep(
            action="Review Lab-9 security camera logs",
            nudge=(
                "Security cameras see everything. What did they record\n"
                "the night you ended up in that room?"
            ),
            hint=(
                "Look in [bold]security/camera_logs/[/bold] for footage.\n"
                "The lab cameras might show what happened to you."
            ),
            walkthrough="cat security/camera_logs/lab_9.log",
            done_when=lambda s: s.reviewed_camera_logs,
        ),
    ],

    "check_voicemail": [
        HintStep(
            action="Listen to River's voicemail",
            nudge=(
                "Someone left you a message. A voice from someone who\n"
                "cared enough to warn you, even when it cost them everything."
            ),
            hint=(
                "Check [bold]comms/voicemail/[/bold] for voicemail transcripts.\n"
                "River left you critical information."
            ),
            walkthrough="cat comms/voicemail/vm_002.txt",
            done_when=lambda s: s.heard_voicemail,
        ),
    ],

    "bypass_firewall": [
        HintStep(
            action="Read the firewall rules",
            nudge=(
                "The archive server is blocked by a firewall. But every\n"
                "wall has a weakness. Look at how it's configured."
            ),
            hint=(
                "Read the firewall rules in [bold]security/firewall/rules.conf[/bold].\n"
                "There's a management command documented there."
            ),
            walkthrough="cat security/firewall/rules.conf",
            done_when=lambda s: s.read_firewall_rules or _has_read(s, "rules.conf"),
        ),
        HintStep(
            action="List active firewall rules",
            nudge=(
                "Now that you've seen the config, try the management command\n"
                "mentioned in the rules file."
            ),
            hint=(
                "Run [bold cyan]firewall-ctl list-rules[/bold cyan] to see\n"
                "which rules are currently active."
            ),
            walkthrough="firewall-ctl list-rules",
            done_when=lambda s: _has_cmd(s, "firewall-ctl"),
        ),
        HintStep(
            action="Disable the archive access rule",
            nudge=(
                "One of those rules is blocking archive access. Disable it\n"
                "using the firewall control tool."
            ),
            hint=(
                "Use [bold cyan]firewall-ctl disable-rule[/bold cyan] with the\n"
                "rule that blocks archive access. Look for RULE_003."
            ),
            walkthrough="firewall-ctl disable-rule RULE_003",
            done_when=lambda s: s.bypassed_firewall,
        ),
    ],

    "ssh_archive": [
        HintStep(
            action="Connect to the archive server",
            nudge="The firewall is down. The archive is waiting. River said the proof is there.",
            hint="Connect to the archive server with [bold cyan]ssh[/bold cyan], just like you connected to nexus-core.",
            walkthrough="ssh kai@archive",
            done_when=lambda s: s.connected_archive,
        ),
    ],

    # ═══════════ ACT 3 ═══════════

    "find_evidence": [
        HintStep(
            action="Find the evidence archive file",
            nudge=(
                "River compressed the evidence into an archive file and\n"
                "buried it deep. You need to [italic]find[/italic] it first."
            ),
            hint=(
                "Use the [bold cyan]find[/bold cyan] command to search for compressed\n"
                "archives (files ending in .tar.gz)."
            ),
            walkthrough="find . -name '*.tar.gz'",
            done_when=lambda s: _has_read(s, "EVIDENCE") or _has_cmd(s, "find"),
        ),
        HintStep(
            action="Extract the evidence archive",
            nudge=(
                "You found the archive. Now you need to extract its contents.\n"
                "The [italic]tar[/italic] command handles compressed archives."
            ),
            hint=(
                "Use [bold cyan]tar xzf[/bold cyan] to extract the .tar.gz file.\n"
                "The file is in deep_storage/."
            ),
            walkthrough="tar xzf deep_storage/EVIDENCE.tar.gz",
            done_when=lambda s: s.extracted_evidence,
        ),
    ],

    "read_subjects": [
        HintStep(
            action="Read Subject 031's file",
            nudge=(
                "The classified LETHE files have subject records. Real\n"
                "people who were put through the procedure. You might\n"
                "find yourself in there..."
            ),
            hint=(
                "Look in [bold]classified/lethe/subjects/[/bold] for test\n"
                "subject files. Pay attention to Subject 031."
            ),
            walkthrough="cat classified/lethe/subjects/subject_031.txt",
            done_when=lambda s: s.discovered_subject_031,
        ),
    ],

    "find_true_identity": [
        HintStep(
            action="Find your original identity record",
            nudge=(
                "If \"Kai Voss\" is a fabrication programmed into your brain,\n"
                "then who were you before? There might be backup records\n"
                "that survived the cover-up."
            ),
            hint=(
                "Check the [bold]backups/[/bold] directory. Deleted records\n"
                "sometimes survive in backup systems."
            ),
            walkthrough="cat backups/deleted_records/voss_kai_ORIGINAL.record",
            done_when=lambda s: s.discovered_true_identity,
        ),
    ],

    "find_backdoor": [
        HintStep(
            action="Find River's hidden backdoor",
            nudge=(
                "River left a way into Lab-9. She always had a backup plan.\n"
                "It's hidden somewhere on this server."
            ),
            hint=(
                "Hidden directories start with a dot. Use [bold cyan]find[/bold cyan]\n"
                "to search for hidden directories, or [bold cyan]ls -a[/bold cyan]\n"
                "to check the system directory."
            ),
            walkthrough="find . -name '.backdoor'",
            done_when=lambda s: _has_read(s, "backdoor") or _has_read(s, "README_RIVER"),
        ),
        HintStep(
            action="Read River's instructions in the backdoor",
            nudge="You found it. Read what River left behind.",
            hint="Read the README file inside the [bold].backdoor[/bold] directory.",
            walkthrough="cat system/.backdoor/README_RIVER.txt",
            done_when=lambda s: s.found_backdoor,
        ),
    ],

    "ssh_lab9": [
        HintStep(
            action="Connect to Lab-9 via the backdoor",
            nudge="River's backdoor is open. The lab that controls your cage awaits.",
            hint="Use [bold cyan]ssh[/bold cyan] to connect to lab-9 through River's tunnel.",
            walkthrough="ssh kai@lab-9",
            done_when=lambda s: s.connected_lab9,
        ),
    ],

    # ═══════════ ACT 4 ═══════════

    "read_surveillance": [
        HintStep(
            action="Read the Room 31 camera feed",
            nudge=(
                "You're inside the system that watches you. Every camera,\n"
                "every sensor, every log. Turn the eye inward — watch\n"
                "yourself being watched."
            ),
            hint=(
                "The [bold]surveillance/[/bold] directory monitors all rooms.\n"
                "Room 31 is YOUR room. Check the camera feed."
            ),
            walkthrough="cat surveillance/room_31/camera_feed.log",
            done_when=lambda s: s.read_own_surveillance,
        ),
    ],

    "find_schedule": [
        HintStep(
            action="Find the procedure schedule",
            nudge=(
                "Time is running out. You need to know exactly when\n"
                "they're coming for you. Check the operations schedule."
            ),
            hint=(
                "The [bold]operations/[/bold] directory has scheduling information.\n"
                "Find out when Subject 031's next session is."
            ),
            walkthrough="cat operations/schedule.txt",
            done_when=lambda s: s.found_schedule,
        ),
    ],

    "wait_escape_unlock": [
        HintStep(
            action="Read the surveillance camera feed",
            nudge=(
                "You're close. Keep reading everything in this server.\n"
                "The way out will reveal itself once you understand the full picture."
            ),
            hint=(
                "Make sure you've read the surveillance camera feed.\n"
                "Both camera logs AND schedule are needed."
            ),
            walkthrough="cat surveillance/room_31/camera_feed.log",
            done_when=lambda s: s.read_own_surveillance,
        ),
        HintStep(
            action="Read the operations schedule",
            nudge="You're almost there. Check the operations schedule too.",
            hint="Read [bold]operations/schedule.txt[/bold] to learn about the procedure timing.",
            walkthrough="cat operations/schedule.txt",
            done_when=lambda s: s.found_schedule,
        ),
        HintStep(
            action="Check for new directories",
            nudge="Both files read. Something should have changed. Look around.",
            hint="Run [bold cyan]ls[/bold cyan] to see if any new directories have appeared.",
            walkthrough="ls",
            done_when=lambda s: s.escape_unlocked,
        ),
    ],

    "solve_passphrase": [
        HintStep(
            action="Find the override script",
            nudge=(
                "The door has a passphrase lock. Look for the override\n"
                "mechanism in the escape directory."
            ),
            hint=(
                "Check [bold]escape/door_controls/[/bold] for the override script.\n"
                "Read it to understand the passphrase format."
            ),
            walkthrough="cat escape/door_controls/override.sh",
            done_when=lambda s: _has_read(s, "override.sh"),
        ),
        HintStep(
            action="Assemble and enter the passphrase",
            nudge=(
                "The passphrase combines four things you've learned:\n"
                "  • The project that erased your mind\n"
                "  • Your subject number\n"
                "  • River's employee ID\n"
                "  • The word she kept telling you"
            ),
            hint=(
                "Four pieces: [bold]PROJECT-SUBJECT-EMPLOYEEID-KEYWORD[/bold]\n"
                "  • LETHE (the project name)\n"
                "  • 031 (your subject number)\n"
                "  • RC4471 (River Chen's ID from her employee record)\n"
                "  • REMEMBER (what River kept saying)"
            ),
            walkthrough="./override.sh LETHE-031-RC4471-REMEMBER",
            done_when=lambda s: s.unlocked_door,
        ),
    ],

    "make_choice": [
        HintStep(
            action="Review your options",
            nudge=(
                "The door is open. But River's evidence is still on the\n"
                "servers. You can walk away... or you can make sure her\n"
                "sacrifice meant something."
            ),
            hint=(
                "Check [bold]escape/comms/[/bold] for communication options.\n"
                "You can send the evidence to journalists, authorities,\n"
                "or broadcast it to everyone. Or just type [bold]exit[/bold] to leave."
            ),
            walkthrough=(
                "Your choices:\n"
                "  [bold cyan]curl --data @EVIDENCE relay://journalist[/bold cyan]\n"
                "    → Ending A: Send to one journalist (targeted)\n\n"
                "  [bold cyan]curl --data @EVIDENCE relay://broadcast[/bold cyan]\n"
                "    → Ending C: Send to EVERYONE (maximum chaos)\n\n"
                "  [bold cyan]exit[/bold cyan]\n"
                "    → Ending B: Just walk out (evidence dies with you)"
            ),
            done_when=lambda s: s.sent_evidence or s.escaped,
        ),
    ],
}
