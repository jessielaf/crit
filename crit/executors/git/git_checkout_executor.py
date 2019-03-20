from dataclasses import dataclass
from typing import List
from crit.executors import SingleExecutor


@dataclass
class GitCheckoutExecutor(SingleExecutor):
    """
    Checkout a version of a repository

    Args:
        version (str): The repository that needs to be pulled. Defaults to :obj:`master`
        force (bool): Force git pull and git clone. Defaults to :obj:`False`
    """

    version: str = 'master'
    force: bool = False

    def commands(self) -> str:
        command = f'git checkout '

        if self.force:
            command += '--force '

        return command + self.version

    def is_changed(self, output: List[str]):
        for line in output:
            if 'Switched to branch' in line:
                return True

        return super().is_changed(output)
