"""Network commands: ssh, ping, curl (all simulated)."""

from __future__ import annotations

import time

from neonvoid.engine.commands.base import CommandContext

# Valid SSH targets and their required flags
SSH_TARGETS = {
    "nexus-core": {
        "users": ["kai", "kvoss", "kai.voss"],
        "required_flag": "found_ssh_creds",
        "server_flag": "connected_nexus_core",
        "act": 2,
    },
    "archive": {
        "users": ["kai", "kvoss", "kai.voss", "root"],
        "required_flag": "bypassed_firewall",
        "server_flag": "connected_archive",
        "act": 3,
    },
    "lab-9": {
        "users": ["kai", "kvoss", "kai.voss", "root", "river"],
        "required_flag": "found_backdoor",
        "server_flag": "connected_lab9",
        "act": 4,
    },
}

# Simulated ping targets
PING_RESPONSES = {
    "nexus-core": "10.0.7.1",
    "nexus-core.omnicron.internal": "10.0.7.1",
    "archive": "10.0.7.50",
    "archive.omnicron.internal": "10.0.7.50",
    "lab-9": "10.0.9.1",
    "lab-9.omnicron.internal": "10.0.9.1",
    "gateway": "10.0.0.1",
    "localhost": "127.0.0.1",
    "10.0.7.1": "10.0.7.1",
    "10.0.7.50": "10.0.7.50",
    "10.0.9.1": "10.0.9.1",
}


class SshCommand:
    name = "ssh"
    aliases = []
    help_text = "Connect to a remote server. Usage: ssh [user@]server"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if not args:
            return "usage: ssh [user@]hostname"

        target = args[0]
        user = "kai"

        if "@" in target:
            user, target = target.split("@", 1)

        # Check if it's a valid target
        if target not in SSH_TARGETS:
            return f"ssh: Could not resolve hostname {target}: Name or service not known"

        server = SSH_TARGETS[target]

        # Check user
        if user not in server["users"]:
            return f"ssh: {user}@{target}: Permission denied (publickey)"

        # Check required flag
        if not ctx.state.get_flag(server["required_flag"]):
            if target == "archive":
                return f"ssh: connect to host {target} port 22: Connection refused"
            elif target == "lab-9":
                return (
                    f"ssh: connect to host {target} port 22: Connection refused\n"
                    f"[dim]The connection was blocked by the network firewall.[/dim]"
                )
            else:
                return f"ssh: {user}@{target}: Permission denied (publickey)"

        # Trigger the SSH connection
        ctx.action = "ssh_connect"
        ctx.action_data = {
            "server": target,
            "user": user,
            "act": server["act"],
            "server_flag": server["server_flag"],
        }

        return f"__SSH_CONNECT__{target}"


class ExitCommand:
    name = "exit"
    aliases = ["logout", "disconnect"]
    help_text = "Disconnect from current server (or quit if on local)."

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if ctx.state.current_server == "local":
            return "[dim]There is nowhere to disconnect to. You are on the local terminal.[/dim]"

        # If on lab-9 with door unlocked but evidence not sent, trigger Ending B
        if (ctx.state.current_server == "lab-9"
                and ctx.state.unlocked_door
                and not ctx.state.sent_evidence):
            ctx.action = "ending_b"
            return "__ENDING_B__"

        ctx.action = "ssh_disconnect"
        return f"__SSH_DISCONNECT__"


class PingCommand:
    name = "ping"
    aliases = []
    help_text = "Check if a host is reachable. Usage: ping <host>"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if not args:
            return "ping: missing host operand"

        host = args[0]
        count = 3

        # Parse -c flag
        for i, arg in enumerate(args):
            if arg == "-c" and i + 1 < len(args):
                try:
                    count = int(args[i + 1])
                except ValueError:
                    pass

        ip = PING_RESPONSES.get(host)
        if ip is None:
            return f"ping: {host}: Name or service not known"

        lines = [f"PING {host} ({ip}): 56 data bytes"]
        for seq in range(count):
            ms = 0.5 + (hash(f"{host}{seq}") % 100) / 100 * 2
            lines.append(f"64 bytes from {ip}: icmp_seq={seq} ttl=64 time={ms:.1f} ms")

        lines.append(f"\n--- {host} ping statistics ---")
        lines.append(f"{count} packets transmitted, {count} received, 0% packet loss")
        return "\n".join(lines)


class CurlCommand:
    name = "curl"
    aliases = ["wget"]
    help_text = "Transfer data to/from a server. Usage: curl [options] <url>"

    def execute(self, args: list[str], ctx: CommandContext) -> str:
        if not args:
            return "curl: missing URL"

        data_file: str | None = None
        url: str | None = None

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ("--data", "-d", "--data-binary"):
                if i + 1 < len(args):
                    i += 1
                    data_file = args[i]
            elif arg.startswith("--data=") or arg.startswith("-d="):
                data_file = arg.split("=", 1)[1]
            elif not arg.startswith("-"):
                url = arg
            i += 1

        if url is None:
            return "curl: missing URL"

        # Handle the evidence sending mechanic
        if "relay://" in url:
            return self._handle_relay(url, data_file, ctx)

        # Generic responses for other URLs
        if "omnicron" in url.lower():
            return (
                "HTTP/1.1 403 Forbidden\n"
                "Server: OmnicronFirewall/7.2\n"
                "Content-Type: text/html\n\n"
                "<html><body><h1>403 Access Denied</h1>"
                "<p>Your access has been logged.</p></body></html>"
            )

        return f"curl: (6) Could not resolve host: {url.split('//')[1].split('/')[0] if '//' in url else url}"

    def _handle_relay(self, url: str, data_file: str | None, ctx: CommandContext) -> str:
        target = url.replace("relay://", "")

        if not ctx.state.unlocked_door:
            return "curl: (7) Failed to connect -- communications relay is offline"

        if data_file is None:
            return "curl: no data specified for relay transmission"

        if target == "journalist" or target == "elena.vasquez":
            ctx.state.sent_evidence = True
            ctx.action = "ending_a"
            return "__ENDING_A__"
        elif target in ("ALL", "all", "broadcast"):
            ctx.state.sent_evidence = True
            ctx.state.sent_evidence_all = True
            ctx.action = "ending_c"
            return "__ENDING_C__"
        elif target == "authorities" or target == "law_enforcement":
            ctx.state.sent_evidence = True
            ctx.action = "ending_a"
            return "__ENDING_A__"
        else:
            return f"curl: relay://{target}: Unknown relay target. Check contacts.txt for valid endpoints."
