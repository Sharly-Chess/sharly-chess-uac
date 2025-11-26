import sys
from pathlib import Path

from uac.win_registry import WinRegistryUtils
from uac.uac import UAC


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

    def add_exclusion(self) -> bool:
        """Add the folder to Windows defender exclusions.
        Returns True on success, False on failure."""
        import subprocess

        cmd: list[str] = [
            'powershell',
            '-Command',
            f'Add-MpPreference -ExclusionPath "{self.folder}"',
        ]
        print(f'Running command [{" ".join(cmd)}]...')
        process = subprocess.run(cmd, capture_output=True, text=True)
        print(f'Command returned [{process.returncode}].')
        print(
            f'stdout={"\n".join(line for line in map(lambda s: s.rstrip(), process.stdout.split("\n")) if line)}'
        )
        print(
            f'stderr={"\n".join(line for line in map(lambda s: s.rstrip(), process.stderr.split("\n")) if line)}'
        )
        return process.returncode == 0

    def _user_check(self) -> None:
        if not Path(self.folder).is_dir():
            raise NotADirectoryError(f'[{sys.argv[0]}] Folder {self.folder} not found.')

    def _admin_check(self) -> None:
        self._user_check()
        if self.folder.lower() in (
            exclusion.lower() for exclusion in self.get_exclusions()
        ):
            raise RuntimeError(
                f'Folder [{self.folder}] is already in the Windows Defender exclusions.'
            )
        return None

    def _run(self) -> None:
        if not self.add_exclusion():
            raise RuntimeError(
                f'Could not add folder [{self.folder}] to the Windows Defender exclusions.'
            )
        print(
            f'Folder [{self.folder}] has been added to the Windows Defender exclusions.'
        )
        for exclusion in self.get_exclusions():
            print(f'- {exclusion}')
        return None
