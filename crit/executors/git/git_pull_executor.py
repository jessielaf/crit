from dataclasses import dataclass
from typing import List

from crit.executors import SingleExecutor


@dataclass
class GitPullExecutor(SingleExecutor):
    """
    Executor that clones and pulls a repository. Via ssh

    Args:
        force (bool): Force git pull and git clone. Defaults to :obj:`False`
    """

    force: bool = False

    def commands(self) -> str:
        command = f'git pull'

        if self.force:
            command += ' --force'

        return command

    def is_changed(self, output: List[str]):
        for line in output:
            if 'Updating' in line:
                return True

        return super().is_changed(output)
