from typing import List
from dataclasses import dataclass
from crit.executors import BaseExecutor

@dataclass
class _Action:
    command: str
    line: str

@dataclass
class AptExecutor(BaseExecutor):
    """
    Install package using the debian package manager

    Args:
        package (str): The package to perform the action on
        sudo (bool): Add sudo before the command. Defaults to :obj:`True`
        action (str): The action to perform. You can choose from :obj:`install`, :obj:`update`, :obj:`remove`, :obj:`purge`. Defaults to :obj:`install`

    Attributes:
        action_to_call (list): Mapping of action to command and the line to check if it was changed
    """

    package: str = None
    sudo: bool = True
    action: str = 'install'

    action_to_call = {
        'install': _Action('install', 'The following NEW packages will be installed:'),
        'update': _Action('--only-upgrade install', 'The following packages will be upgraded:'),
        'purge': _Action('purge', 'The following packages will be REMOVED:'),
        'remove': _Action('remove', 'The following packages will be REMOVED:'),
    }

    def commands(self):
        """
        Creates the command for the AptExecutor

        Args:
            host: Host on which the command is ran

        Returns:
            Command that installs the package
        """

        # Add frontend check https://askubuntu.com/questions/506158/unable-to-initialize-frontend-dialog-when-using-ssh
        command = f'DEBIAN_FRONTEND="noninteractive" apt-get -y {self.action_to_call[self.action].command} {self.package}'

        return command

    def changed(self, text: List[str]):
        """
        Checks if via the output if the status is changed. This is checked via the action_to_call variable

        Args:
            text: The output of the command

        Returns:
            If the status has changed
        """

        line_expected = self.action_to_call[self.action].line

        for line in text:
            if line_expected in line:
                return True

        return False
