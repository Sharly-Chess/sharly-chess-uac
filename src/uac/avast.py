import json
import re
import sys
from pathlib import Path

from uac.uac import UAC
from uac.win_registry import WinRegistryUtils


class AvastUAC(UAC):
    @property
    def id(self) -> str:
        return 'avast'

    @property
    def name(self) -> str:
        return 'Avast'

    def _get_exclusions(
        self,
    ) -> list[str]:
        """Returns all the Avast exclusions."""
        exclusions: list[str] = []
        value: str = WinRegistryUtils.get_hklm_value(
            r'SOFTWARE\Avast Software\Avast\properties\exclusions\Global',
            'ExcludeFiles',
        )
        if value:
            for string_part in value.split(';'):
                if matches := re.match(r'^"([^"]+)"$', string_part):
                    exclusions.append(matches.group(1))
                else:
                    print(f'Unrecognised string [{string_part}]')
        if exclusions:
            print('Avast exclusions are:')
            for exclusion in exclusions:
                print(f'- {exclusion}')
        else:
            print('No Avast exclusions found.')
        return exclusions

    def _add_exclusion(self):
        """Add the folder to the Avast exclusions."""
        print('Checking that the exclusion has not been already set...')
        exclusions: list[str] = self._get_exclusions()
        if f'{str(self.folder).lower()}\\*' in (
            exclusion.lower() for exclusion in exclusions
        ):
            print(
                f'Folder [{self.folder}] has already been added to the Avast exclusions.'
            )
        else:
            print(f'Adding folder [{self.folder}] to the exclusions...')
            WinRegistryUtils.set_hklm_sz(
                r'SOFTWARE\Avast Software\Avast\properties\exclusions\Global',
                'ExcludeFiles',
                ';'.join(
                    [
                        f'"{exclusion}"'
                        for exclusion in exclusions
                        + [
                            f'{self.folder}\\*',
                        ]
                    ]
                ),
            )
            print('Checking the the exclusion has been correctly added...')
            exclusions: list[str] = self._get_exclusions()
            if f'{str(self.folder).lower()}\\*' not in (
                exclusion.lower() for exclusion in exclusions
            ):
                raise RuntimeError(
                    f'Folder [{self.folder}] could not be added to the Avast exclusions.'
                )
        marker_file: Path = self.tmp_dir / f'{self.id}.json'
        print(f'Writing marker file [{marker_file}]...')
        with open(marker_file, 'w', encoding='utf-8') as file:
            json.dump(str(self.folder), file)

    def _run(self):
        print(f'Checking folder [{self.folder}]...')
        if not self.folder.is_dir():
            raise NotADirectoryError(f'[{sys.argv[0]}] Folder {self.folder} not found.')
        self._add_exclusion()
        print(f'Folder [{self.folder}] has been added to the Avast exclusions.')
