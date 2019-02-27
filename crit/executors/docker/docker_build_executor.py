from dataclasses import dataclass
from crit.executors import SingleExecutor


@dataclass
class DockerBuildExecutor(SingleExecutor):
    """
    Args:
        tag (str): Name and tag for the docker contianer. :obj:`Optional`
        memory (str): Memory the docker build command should use. :obj:`Optional`
    """

    tag: str = ''
    memory: str = ''

    def commands(self):
        command = 'docker build'

        if self.tag:
            command += f' --tag {self.tag}'

        if self.memory:
            command += f' --memory {self.memory}'

        return command + ' .'
