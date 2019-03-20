import re
from dataclasses import dataclass
from typing import List

from crit.executors import SingleExecutor


@dataclass
class GitCloneExecutor(SingleExecutor):
    """
    Executor that clones and pulls a repository. Via ssh

    Args:
        repository (str): The repository that needs to be pulled :obj:`required`
    """

    repository: str = None

    def commands(self) -> str:
        return f'git clone {self.repository}'

    def catched_error(self, output: List[str]):
        regexp = re.compile(r'fatal: destination path .* already exists and is not an empty directory')

        if len(output) > 0 and regexp.search(output[0]):
            return True

        return super().catched_error(output)

    def is_changed(self, output: List[str]):
        for line in output:
            if 'Cloning into' in line:
                return True

        return super().is_changed(output)
