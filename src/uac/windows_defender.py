import os
import subprocess
import sys
from pathlib import Path

from uac.uac import UAC
from uac.win_registry import WinRegistryUtils


class WindowsDefenderUAC(UAC):
    def __init__(
        self,
        folder: str,
    ):
        super().__init__()
        self.folder = folder.rstrip('\\')

    @staticmethod
    def get_exclusions() -> list[str]:
        """Returns all Windows Defender exclusions."""
        return list(
            WinRegistryUtils.get_registry_hklm_values(
                r'SOFTWARE\Microsoft\Windows Defender\Exclusions\Paths'
            ).keys()
        )

    def add_exclusion(self):
        """Add the folder to Windows defender exclusions.
        Returns True on success, False on failure."""

        if not (win_dir := os.environ.get('windir')):
            raise EnvironmentError(
                f'Environment variable [windir] not set, can not locate conhost.exe to add folder [{self.folder}] to the Windows Defender exclusions.\n'
            )
        conhost_path: Path = Path(win_dir) / 'system32/conhost.exe'
        if not conhost_path.is_file():
            raise FileNotFoundError(
                f'Program [{conhost_path}] not found, can not add folder [{self.folder}] to the Windows Defender exclusions.\n'
            )
        cmd: list[str] = [
            'cmd',
            '/c',
            'start',
            '/min',
            'powershell.exe',
            '-WindowStyle',
            'hidden',
            '-Command',
            f'Add-MpPreference -ExclusionPath "{self.folder}"',
        ]
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode:
            raise RuntimeError(
                f'Could not add folder [{self.folder}] to the Windows Defender exclusions.\n'
                f'Command [{" ".join(cmd)}] returned [{process.returncode}]\n'
                f'stdout={"\n".join(line for line in map(lambda s: s.rstrip(), process.stdout.split("\n")) if line)}\n'
                f'stderr={"\n".join(line for line in map(lambda s: s.rstrip(), process.stderr.split("\n")) if line)}\n'
            )

    def _user_check(self):
        if not Path(self.folder).is_dir():
            raise NotADirectoryError(f'[{sys.argv[0]}] Folder {self.folder} not found.')

    def _admin_check(self):
        self._user_check()
        if self.folder.lower() in (
            exclusion.lower() for exclusion in self.get_exclusions()
        ):
            raise RuntimeError(
                f'Folder [{self.folder}] is already in the Windows Defender exclusions.'
            )
        return None

    def _run(self):
        self.add_exclusion()
        print(
            f'Folder [{self.folder}] has been added to the Windows Defender exclusions.'
        )
        for exclusion in self.get_exclusions():
            print(f'- {exclusion}')
