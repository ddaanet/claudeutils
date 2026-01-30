"""Keychain wrapper for macOS security command."""

import subprocess


class Keychain:
    """Wrapper for macOS Keychain security commands."""

    def find(self, account: str, service: str) -> str:
        """Find password in keychain.

        Args:
            account: Account name to search for
            service: Service name to search for

        Returns:
            Password string from keychain
        """
        result = subprocess.run(
            ["security", "find-generic-password", "-a", account, "-s", service, "-w"],
            capture_output=True,
            text=False,
            check=False,
        )

        # Extract password from output (remove newline if present)
        return result.stdout.decode("utf-8").strip()
