import os
import subprocess
import sys
from pathlib import Path

from uac.uac import UAC
from uac.win_registry import WinRegistryUtils


class WindowsDefenderUAC(UAC):
    @property
    def id(self) -> str:
        return 'avast'

    @property
    def name(self) -> str:
        return 'Avast'

    @staticmethod
    def get_exclusions() -> list[str]:
        """Returns all the Windows Defender exclusions."""
        if exclusions := list(
            WinRegistryUtils.get_hklm_values(
                r'SOFTWARE\Microsoft\Windows Defender\Exclusions\Paths'
            ).keys()
        ):
            print('Windows Defender exclusions are:')
            for exclusion in exclusions:
                print(f'- {exclusion}')
        else:
            print('No Windows Defender exclusions found.')
        return exclusions

    def add_exclusion(self):
        """Add the folder to the Windows defender exclusions."""
        print('Checking that the exclusion has not been already set...')
        if str(self.folder).lower() in (
            exclusion.lower() for exclusion in self.get_exclusions()
        ):
            raise RuntimeError(
                f'Folder [{self.folder}] is already in the Windows Defender exclusions.'
            )
        windir_var_name: str = 'windir'
        print(f'Testing env variable [{windir_var_name}]...')
        if not (win_dir := os.environ.get(windir_var_name)):
            raise EnvironmentError(
                f'Environment variable [{windir_var_name}] not set, can not locate conhost.exe to add folder [{self.folder}] to the Windows Defender exclusions.\n'
            )
        conhost_path: Path = Path(win_dir) / 'system32/conhost.exe'
        print(f'Searching for [{conhost_path.name}]...')
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
        print(f'Running command [{" ".join(cmd)}]...')
        process = subprocess.run(cmd, capture_output=True, text=True)
        print(f'Command returned [{process.returncode}].')
        if process.returncode:
            raise RuntimeError(
                f'Could not add folder [{self.folder}] to the Windows Defender exclusions.\n'
                f'Command [{" ".join(cmd)}] returned [{process.returncode}]\n'
                f'stdout={"\n".join(line for line in map(lambda s: s.rstrip(), process.stdout.split("\n")) if line)}\n'
                f'stderr={"\n".join(line for line in map(lambda s: s.rstrip(), process.stderr.split("\n")) if line)}\n'
            )

    def _run(self):
        print(f'Checking folder [{self.folder}]...')
        if not self.folder.is_dir():
            raise NotADirectoryError(f'[{sys.argv[0]}] Folder {self.folder} not found.')
        self.add_exclusion()
        print(
            f'Folder [{self.folder}] has been added to the Windows Defender exclusions.'
        )
