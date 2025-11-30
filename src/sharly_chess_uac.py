import argparse
import importlib.metadata
import sys
from argparse import ArgumentError
from pathlib import Path

from packaging.version import Version

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
    parser.add_argument(
        '--avast-exclude',
        type=str,
    )
    args = parser.parse_args()
    if args.windows_defender_exclude:
        from uac.windows_defender import WindowsDefenderUAC

        WindowsDefenderUAC(args.windows_defender_exclude).run_as_admin()
    elif args.avast_exclude:
        from uac.avast import AvastUAC

        AvastUAC(args.avast_exclude).run_as_admin()
    else:
        raise ArgumentError(None, f'[{sys.argv[0]}]: no parameter provided.')


if __name__ == '__main__':
    main()
