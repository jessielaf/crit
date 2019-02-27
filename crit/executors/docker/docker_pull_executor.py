from dataclasses import dataclass
from crit.executors import SingleExecutor


@dataclass
class DockerPullExecutor(SingleExecutor):
    """
    WARNING NOT TESTED
    """

    image: str = ''
    extra_commands: str = ''

    def commands(self):
        return f'docker pull {self.extra_commands} {self.image}'
