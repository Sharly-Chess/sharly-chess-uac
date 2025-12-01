import platform
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from subprocess import list2cmdline
from time import sleep

from tee import StdoutTee, StderrTee


def is_user_admin() -> bool:
    """Check if the current OS user is an Administrator or root.
    :return: True if the current user is an 'Administrator', otherwise False."""
    if platform.system() != 'Windows':
        raise NotImplementedError('This function is only implemented on Windows.')

    import win32security

    try:
        print('Calling CreateWellKnownSid()...')
        admin_sid = win32security.CreateWellKnownSid(
            win32security.WinBuiltinAdministratorsSid,
            None,
        )
        print(f'CreateWellKnownSid() returned [{admin_sid}].')
        print('Calling CheckTokenMembership()...')
        return_value = win32security.CheckTokenMembership(0, admin_sid)
        print(f'CheckTokenMembership() returned [{return_value}].')
        return return_value
    except Exception as e:
        print(f'Admin check failed, assuming not an admin: {e}.')
        return False


def run_as_admin() -> int:
    if platform.system() != 'Windows':
        raise NotImplementedError('This function is only implemented on Windows.')

    import win32con
    import win32event
    import win32process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon

    if getattr(sys, 'frozen', False):
        cmd_line = sys.argv
    else:
        cmd_line = [sys.executable] + sys.argv
    sleep(2)

    lp_verb: str = 'runas'  # causes UAC elevation prompt.

    cmd = cmd_line[0]
    params = list2cmdline(cmd_line[1:])

    print(f'Running command {cmd}({params})...')
    process_info = ShellExecuteEx(
        # nShow=win32con.SW_SHOWNORMAL,
        nShow=win32con.SW_HIDE,
        fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
        lpVerb=lp_verb,
        lpFile=cmd,
        lpParameters=params,
    )

    # Wait for the process to finish
    process_handle = process_info['hProcess']
    _ = win32event.WaitForSingleObject(process_handle, win32event.INFINITE)
    return_code = win32process.GetExitCodeProcess(process_handle)
    print(f'Process handle {process_handle} returned code {return_code}')

    return return_code


class UACResult:
    def __init__(
        self,
        result: int = 0,
        stdout_str: str = '',
        stderr_str: str = '',
    ):
        self.result: int = result
        self.stdout: str = stdout_str
        self.stderr: str = stderr_str

    def __str__(self):
        return (
            f'result={self.result}, stdout=\n[{self.stdout}], stderr=\n[{self.stderr}]'
        )


class UAC(ABC):
    """An abstract class that asks for admin privileges to execute its run() method."""

    def __init__(
        self,
        folder: str,
    ):
        self.folder: Path = Path(folder.rstrip('\\'))
        self.tmp_dir: Path = Path(self.folder) / f'tmp/antivirus/{self.id}'
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def run_as_admin(self) -> UACResult:
        """Runs with administrator rights (or reload to)."""
        stdout_tmp_file: Path = self.tmp_dir / 'stdout.txt'
        stderr_tmp_file: Path = self.tmp_dir / 'stderr.txt'
        if is_user_admin():
            print('Administrator privileges.')
            with (
                StdoutTee(stdout_tmp_file, mode='a', buff=1),
                StderrTee(stderr_tmp_file, mode='a', buff=1),
            ):
                try:
                    uac_result: UACResult = UACResult(
                        result=self._run() or 0,
                    )
                    print(f'Function returned [{uac_result.result}]')
                    return uac_result
                except Exception as e:
                    print(f'Error running function as admin: {e}')
                    raise
        else:
            print('User privileges, requesting Administrator rights...')
            uac_result: UACResult = UACResult(
                result=run_as_admin(),
            )
            print('Back to user mode to collect result.')
            for is_stdout, file, handle in (
                (True, stdout_tmp_file, sys.stdout),
                (False, stderr_tmp_file, sys.stderr),
            ):
                if file.is_file():
                    with open(file, 'r') as log_fh:
                        console_output = log_fh.read()
                    file.unlink(missing_ok=True)
                    if is_stdout:
                        uac_result.stdout = console_output
                    else:
                        uac_result.stderr = console_output
                    handle.write(console_output)
                    handle.flush()
            return uac_result

    @abstractmethod
    def _run(self):
        """Does the job (with administrator rights).
        This method should throw an exception on error."""
        pass
