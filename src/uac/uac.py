import ctypes
import sys
from abc import ABC, abstractmethod


class UAC(ABC):
    """An abstract class that asks for admin privileges to execute its run() method."""

    def run_as_admin(self):
        """Runs with administrator rights, cf https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script/41930586#41930586"""
        admin: bool = False
        try:
            admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            print(f'Exception raised while controlling administrator rights: {e}')
        if not admin:
            self._user_check()
            ctypes.windll.shell32.ShellExecuteW(
                None, 'runas', sys.executable, ' '.join(sys.argv[1:]), None, 1
            )
        else:
            self._admin_check()
            self._run()

    def _user_check(self):
        """Checks that everything is good before asking to run with administrator rights.
        This method should throw an exception on error."""
        pass

    def _admin_check(self):
        """Checks that everything is good once running with administrator rights.
        This method should throw an exception on error."""
        pass

    @abstractmethod
    def _run(self):
        """Does the job (with administrator rights).
        Returns an error message on failure or None on success."""
        pass
