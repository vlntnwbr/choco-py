"""Application for choco-py"""

import ctypes
import os
import re
import subprocess
import sys
from typing import Union

from .win10toast import ToastNotifier


class ChocoPy(ToastNotifier):
    """ChocoPy Application."""

    def __init__(self):

        super().__init__()
        self.error = None
        self.outdated = self._get_outdated()
        self.icon = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "res", "choco-py.ico"
        )

    def _get_outdated(self) -> Union[int, None]:
        """Determine number of outdated chocolatey packages."""

        try:
            process = subprocess.run(
                "choco outdated",
                capture_output=True,
                text=True,
                check=True,
                shell=True  # No extra console window for gui_script
            )

        except FileNotFoundError:  # choco is not installed
            self.error = "Could not locate Chocolatey."
            return None

        except subprocess.CalledProcessError as exc:
            self.error = f"'{exc.cmd} exited with code {exc.returncode}."
            return None

        outdated = re.findall(r"\b\d+\b", process.stdout.splitlines()[-1])
        return int(outdated[0])

    def notify(self, text: str = None, clickable: bool = True) -> None:
        """Show a choco-py notification"""

        if text is None:

            base = "Chocolatey has determined {count} package{num} outdated."
            if self.outdated == 1:
                num_verb = " is"
            else:
                num_verb = "s are"
            message = base.format(count=self.outdated, num=num_verb)

            if self.outdated > 0:
                message += " Click to upgrade."
            else:
                clickable = False

        self.show_toast(
            title="Choco Py",
            msg=message,
            icon_path=self.icon,
            duration=None,
            callback_on_click=self.start_upgrade if clickable is True else None
        )


    @staticmethod
    def start_upgrade():
        """Execute choco upgrade with elevated privileges."""

        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", "choco", "upgrade all", None, 3
        )


def main():
    """Entrypoint for choco-py."""

    choco = ChocoPy()

    if choco.outdated is None:
        choco.notify(choco.error, False)
        sys.exit(choco.error)

    choco.notify()


if __name__ == "__main__":
    main()
