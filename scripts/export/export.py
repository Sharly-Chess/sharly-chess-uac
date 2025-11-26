import os
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from PyInstaller.__main__ import run

from sharly_chess_uac import SHARLY_CHESS_UAC_VERSION, BASE_DIR

sys.path.extend(
    map(
        str,
        [
            Path(__file__).parents[2],  # The root path
            Path(__file__).parents[2]
            / 'src',  # The path to the sources of the application
            Path(__file__).parents[2]
            / 'scripts/export',  # The path to the scripts of the application
        ],
    )
)


def shutil_delete_onerror(func, path, exc_info):
    """
    This method is used as a workaround for ``PermissionError: access denied``
    errors happening on some Windows systems.
    Usage : ``shutil.rmtree(path, onerror=shutil_delete_onerror)``
    """
    import stat
    import os

    os.chmod(path, stat.S_IWUSR)
    func(path)


def _delete_folder(
    folder: Path,
):
    if folder.is_dir():
        print(f'Deleting folder [{folder}]...')
        shutil.rmtree(folder, onerror=shutil_delete_onerror)


def _delete_file(
    file: Path,
):
    if file.is_file():
        print(f'Deleting file [{file}]...')
        file.unlink()


basename: str = f'sharly_chess_uac-{SHARLY_CHESS_UAC_VERSION}'

build_dir: Path = BASE_DIR / 'build'
_delete_folder(build_dir)
dist_dir: Path = BASE_DIR / 'dist'
_delete_folder(dist_dir)
exe_file: Path = dist_dir / f'sharly_chess_uac-{SHARLY_CHESS_UAC_VERSION}.exe'
_delete_file(exe_file)
zip_file: Path = dist_dir / f'{basename}.zip'
_delete_file(zip_file)

run(
    [
        '--clean',
        '--onefile',
        '--noconfirm',
        f'--name={basename}',
        '--copy-metadata',
        'sharly_chess_uac',
        '--paths=.',
        '--optimize',
        '1',
        'src/sharly_chess_uac.py',
        '--windowed',
        '--icon=src/sharly-chess.ico',
    ]
)

zip_file.parent.mkdir(parents=True, exist_ok=True)

with ZipFile(zip_file, 'w', ZIP_DEFLATED) as zf:
    cwd: str = os.getcwd()
    os.chdir(dist_dir)
    zf.write(exe_file.name)
    os.chdir(cwd)

_delete_folder(build_dir)
