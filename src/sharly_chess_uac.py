import argparse
import importlib.metadata
import sys
from pathlib import Path
from time import sleep

from packaging.version import Version

from uac.windows_defender import WindowsDefenderUAC

APP_NAME: str = 'sharly-chess-uac'
SHARLY_CHESS_UAC_VERSION: Version = Version(importlib.metadata.version(APP_NAME))
DEVEL_ENV: bool = not getattr(sys, 'frozen', False)


def app_base_dir() -> Path:
    """
    Return the directory that holds bundled resources for:
      - Dev:      repo/source tree
      - Onefile:  sys._MEIPASS
    """

    # PyInstaller onefile
    if meipass := getattr(sys, '_MEIPASS', None):
        return Path(meipass)

    # Other frozen (non-.app) onedir
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent

    # Devel env
    return Path(__file__).resolve().parents[1]


BASE_DIR: Path = app_base_dir()

if DEVEL_ENV:
    import tomllib
    from contextlib import suppress

    with suppress(KeyError):
        with open(BASE_DIR / 'pyproject.toml', 'rb') as f:
            version = tomllib.load(f)['project']['version']
        if Version(version) != SHARLY_CHESS_UAC_VERSION:
            print(
                f'Installed {APP_NAME} version {SHARLY_CHESS_UAC_VERSION} does not match defined '
                f'version {version}. Run `pip install -e .` then run {APP_NAME} again.',
                APP_NAME,
                SHARLY_CHESS_UAC_VERSION,
                version,
                APP_NAME,
            )
            raise ValueError(f'{SHARLY_CHESS_UAC_VERSION=}, {version=}')


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '--windows-defender-exclude',
        type=str,
    )
    args = parser.parse_args()
    if args.windows_defender_exclude:
        WindowsDefenderUAC(args.windows_defender_exclude).run_as_admin()
    else:
        raise RuntimeError(f'[{sys.argv[0]}]: no parameter provided.')


if __name__ == '__main__':
    try:
        main()
        # Wait 2 seconds to let the users see eventual success messages.
        sleep(2)
    except Exception as e:
        print(f'Error: {e}')
        input('Type Enter to close this window.')
        raise
