from dataclasses import dataclass
from crit.executors import BaseExecutor


@dataclass
class DockerPullExecutor(BaseExecutor):
    """
    WARNING NOT TESTED
    """

    image: str = ''
    extra_commands: str = ''

    def commands(self):
        return f'docker pull ${self.extra_commands} ${self.image}'
