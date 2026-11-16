"""Defensive SSH diagnostics for a configured Kali VM only.

Host keys must exist in the supplied known_hosts file. Commands are fixed constants;
model-generated command strings are never accepted.
"""
from __future__ import annotations
from pathlib import Path

ALLOWED_DIAGNOSTICS = {
    "system_info": "uname -a",
    "network_interfaces": "ip -brief address",
    "listening_sockets": "ss -lnt",
}

class KaliSSH:
    def __init__(self, hostname: str, username: str, known_hosts: str | Path, key_filename: str | Path, port: int = 22, timeout: int = 10):
        self.hostname, self.username = hostname, username
        self.known_hosts, self.key_filename = str(known_hosts), str(key_filename)
        self.port, self.timeout = port, timeout

    def run_diagnostic(self, diagnostic: str, *, approved: bool) -> str:
        if not approved:
            raise PermissionError("User approval is required for SSH access")
        if diagnostic not in ALLOWED_DIAGNOSTICS:
            raise ValueError("Unsupported diagnostic")
        try:
            import paramiko
        except ImportError as exc:
            raise RuntimeError("Install the optional 'ssh' extra to use SSH") from exc
        client = paramiko.SSHClient()
        client.load_host_keys(self.known_hosts)
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            client.connect(self.hostname, port=self.port, username=self.username, key_filename=self.key_filename, timeout=self.timeout, look_for_keys=False, allow_agent=False)
            _, stdout, stderr = client.exec_command(ALLOWED_DIAGNOSTICS[diagnostic], timeout=self.timeout)
            result = stdout.read().decode("utf-8", errors="replace")
            error = stderr.read().decode("utf-8", errors="replace")
            if error:
                result += "\n" + error
            return result
        finally:
            client.close()
