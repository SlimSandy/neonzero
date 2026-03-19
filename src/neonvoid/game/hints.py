"""Context-sensitive hint system with 3 tiers: vague -> moderate -> specific."""

from __future__ import annotations

from neonvoid.game.state import GameState


class HintSystem:
    """Provides contextual hints based on current game state."""

    def __init__(self):
        self._hint_counts: dict[str, int] = {}

    def get_hint(self, state: GameState) -> str:
        """Get a hint appropriate to the player's current progress."""
        state.hints_used += 1

        # Determine what the player should be doing next
        hint_key = self._get_current_objective(state)
        self._hint_counts[hint_key] = self._hint_counts.get(hint_key, 0) + 1
        tier = min(self._hint_counts[hint_key], 3)

        hints = HINTS.get(hint_key, {})
        hint_text = hints.get(tier, "[dim]No hint available for current state.[/dim]")

        tier_labels = {1: "VAGUE", 2: "MODERATE", 3: "SPECIFIC"}
        label = tier_labels.get(tier, "")

        return (
            f"[dim cyan]── HINT ({label}) ──[/dim cyan]\n"
            f"{hint_text}\n"
            f"[dim]Type 'hint' again for more detail.[/dim]"
        )

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


HINTS: dict[str, dict[int, str]] = {
    # ═══ ACT 1 ═══
    "explore_start": {
        1: "[dim]Look around. What's in this room?[/dim]",
        2: "[dim]Try using [bold]ls[/bold] to see what files and directories are here.[/dim]",
        3: "[dim]Type [bold]ls[/bold] to list files, then [bold]cd desktop[/bold] and [bold]cat README.txt[/bold].[/dim]",
    },
    "find_identity": {
        1: "[dim]The README mentioned checking your messages.[/dim]",
        2: "[dim]There should be a mail directory. Navigate to your inbox.[/dim]",
        3: "[dim]Type [bold]cd mail/inbox[/bold] then [bold]cat 001_welcome.msg[/bold].[/dim]",
    },
    "read_emails": {
        1: "[dim]Read all your messages. Someone sent you something urgent.[/dim]",
        2: "[dim]There are more messages in your inbox. Read them all.[/dim]",
        3: "[dim]Type [bold]cat 003_urgent.msg[/bold] to read the urgent message from 'R'.[/dim]",
    },
    "find_deleted": {
        1: "[dim]The urgent message said 'delete everything.' But did they really delete everything?[/dim]",
        2: "[dim]Some files are hidden. The [bold]ls -a[/bold] command reveals hidden files and directories.[/dim]",
        3: "[dim]Go to the mail directory and type [bold]ls -a[/bold]. You'll find a .deleted folder.[/dim]",
    },
    "find_ssh_creds": {
        1: "[dim]The deleted messages contain valuable information. Read them all carefully.[/dim]",
        2: "[dim]One of the deleted messages has network credentials.[/dim]",
        3: "[dim]In mail/.deleted/, [bold]cat 005_coordinates.msg[/bold] for SSH access credentials.[/dim]",
    },
    "search_lethe": {
        1: "[dim]The name 'LETHE' keeps coming up. Search for more information about it.[/dim]",
        2: "[dim]You can search through file contents with [bold]grep[/bold]. Try searching the logs.[/dim]",
        3: "[dim]Type [bold]grep -ri \"lethe\" logs/[/bold] to search all log files for LETHE references.[/dim]",
    },
    "unlock_lethe": {
        1: "[dim]There's a document about Project LETHE, but it's locked.[/dim]",
        2: "[dim]Check file permissions with [bold]ls -l docs/[/bold]. One file has restricted access.[/dim]",
        3: "[dim]Type [bold]chmod +r docs/project_lethe_summary.txt[/bold] to make it readable.[/dim]",
    },
    "read_lethe": {
        1: "[dim]You unlocked the file. Now read it.[/dim]",
        2: "[dim]Use cat to read the LETHE summary document.[/dim]",
        3: "[dim]Type [bold]cat docs/project_lethe_summary.txt[/bold].[/dim]",
    },
    "map_network": {
        1: "[dim]You have SSH credentials. But where do they lead?[/dim]",
        2: "[dim]Check the network configuration files to find server addresses.[/dim]",
        3: "[dim]Type [bold]cat network/hosts[/bold] and [bold]cat .ssh/config[/bold].[/dim]",
    },
    "ssh_nexus": {
        1: "[dim]You have everything you need to reach the corporate server.[/dim]",
        2: "[dim]Use the [bold]ssh[/bold] command to connect to the server you found.[/dim]",
        3: "[dim]Type [bold]ssh kai@nexus-core[/bold] to connect.[/dim]",
    },

    # ═══ ACT 2 ═══
    "investigate_river": {
        1: "[dim]Who is 'R' from those emails? The company keeps records on everyone.[/dim]",
        2: "[dim]Check the HR department for employee records.[/dim]",
        3: "[dim]Navigate to [bold]hr/employees/[/bold] and look for files related to 'Chen' or 'River'.[/dim]",
    },
    "read_chats": {
        1: "[dim]People talk. Their conversations might reveal what really happened.[/dim]",
        2: "[dim]The comms directory has internal chat logs. Try filtering for relevant names.[/dim]",
        3: "[dim]Try [bold]cat comms/internal_chat/project_lethe.log | grep \"Chen\"[/bold].[/dim]",
    },
    "find_finances": {
        1: "[dim]Follow the money. Corruption always leaves a paper trail.[/dim]",
        2: "[dim]The finance directory has budget records and transaction logs.[/dim]",
        3: "[dim]Read [bold]finance/transactions/offshore_transfers.log[/bold] and compare with budgets using [bold]diff[/bold].[/dim]",
    },
    "check_cameras": {
        1: "[dim]Security cameras see everything. What did they record?[/dim]",
        2: "[dim]Check the security/camera_logs/ directory.[/dim]",
        3: "[dim]Type [bold]cat security/camera_logs/lab_9.log[/bold] for crucial footage.[/dim]",
    },
    "check_voicemail": {
        1: "[dim]Someone left you a message. A voice from beyond.[/dim]",
        2: "[dim]Check the voicemail transcripts in comms/voicemail/.[/dim]",
        3: "[dim]Type [bold]cat comms/voicemail/vm_002.txt[/bold]. River left you directions.[/dim]",
    },
    "bypass_firewall": {
        1: "[dim]The archive server is blocked. But firewalls have rules, and rules have exceptions.[/dim]",
        2: "[dim]Examine the firewall configuration in security/firewall/.[/dim]",
        3: "[dim]Read [bold]security/firewall/rules.conf[/bold]. Use the [bold]firewall-ctl[/bold] command documented there to disable the block.[/dim]",
    },
    "ssh_archive": {
        1: "[dim]The path to the archive is clear now. River said the proof is there.[/dim]",
        2: "[dim]Connect to the archive server with SSH.[/dim]",
        3: "[dim]Type [bold]ssh kai@archive[/bold].[/dim]",
    },

    # ═══ ACT 3 ═══
    "find_evidence": {
        1: "[dim]River hid proof here. It's compressed and buried deep.[/dim]",
        2: "[dim]Use [bold]find[/bold] to locate the evidence archive. Try searching for tar files.[/dim]",
        3: "[dim]Type [bold]find . -name '*.tar.gz'[/bold] then [bold]tar xzf[/bold] the archive you find.[/dim]",
    },
    "read_subjects": {
        1: "[dim]The classified LETHE files contain subject records. You are one of them.[/dim]",
        2: "[dim]Look in classified/lethe/subjects/ for test subject files.[/dim]",
        3: "[dim]Read [bold]classified/lethe/subjects/subject_031.txt[/bold]. Subject 031 is you.[/dim]",
    },
    "find_true_identity": {
        1: "[dim]If Kai Voss is a fabrication... who are you really?[/dim]",
        2: "[dim]There might be backup records that show your original identity.[/dim]",
        3: "[dim]Check [bold]backups/deleted_records/[/bold] for your original employee record. Use [bold]diff[/bold] to compare.[/dim]",
    },
    "find_backdoor": {
        1: "[dim]River left a way into the lab. She always had a backup plan.[/dim]",
        2: "[dim]Hidden directories can be found with [bold]find[/bold] or [bold]ls -a[/bold].[/dim]",
        3: "[dim]Type [bold]find . -name '.backdoor'[/bold] or check [bold]ls -aR system/[/bold].[/dim]",
    },
    "ssh_lab9": {
        1: "[dim]You have River's backdoor. The lab awaits.[/dim]",
        2: "[dim]Read the README in the backdoor directory for connection instructions.[/dim]",
        3: "[dim]Type [bold]ssh kai@lab-9[/bold] using River's tunnel.[/dim]",
    },

    # ═══ ACT 4 ═══
    "read_surveillance": {
        1: "[dim]You're inside the system that watches you. Turn the eye inward.[/dim]",
        2: "[dim]The surveillance directory monitors all rooms. Including yours.[/dim]",
        3: "[dim]Type [bold]cat surveillance/room_31/camera_feed.log[/bold].[/dim]",
    },
    "find_schedule": {
        1: "[dim]Time is running out. Find out exactly how much you have left.[/dim]",
        2: "[dim]The operations directory has scheduling information.[/dim]",
        3: "[dim]Type [bold]cat operations/schedule.txt[/bold].[/dim]",
    },
    "wait_escape_unlock": {
        1: "[dim]Keep exploring. The way out will reveal itself.[/dim]",
        2: "[dim]Make sure you've read the surveillance feed AND the schedule.[/dim]",
        3: "[dim]Once you've read both the camera feed and the schedule, look for an escape route.[/dim]",
    },
    "solve_passphrase": {
        1: "[dim]The door requires a passphrase. The answer is scattered across everything you've learned.[/dim]",
        2: "[dim]Read the lock system config for a hint. The passphrase combines: the project name, your subject number, River's ID, and a keyword.[/dim]",
        3: "[dim]The passphrase is: [bold]LETHE-031-RC4471-REMEMBER[/bold]. Run the override script with it.[/dim]",
    },
    "make_choice": {
        1: "[dim]The door is open. But the evidence is still here. What will you do with it?[/dim]",
        2: "[dim]Check escape/comms/ for communication options. You can send the evidence before you leave.[/dim]",
        3: "[dim]Use [bold]curl --data @EVIDENCE relay://journalist[/bold] to send evidence, or type [bold]exit[/bold] to just escape.[/dim]",
    },
}
