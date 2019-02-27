from typing import Dict, List
from dataclasses import dataclass
from crit.executors import SingleExecutor


@dataclass
class DockerRunExecutor(SingleExecutor):
    """
    Args:
        image (str): The image which should be pulled and the command that should be ran on the command. :obj:`required`
        name (str): The name that will be given to the image. :obj:`optional`
        volumes (Dict[str, str]): Volumes which should be mounted. Key is the host-src and the value is the container-src. :obj:`optional`
        ports (Dict[str, str]): Ports which should be exposed. Key is the host-post and the value is the container-post. :obj:`optional`
        detached (bool): Run in detached mode. Defaults to :obj:`True`
        tty (bool): Run in tty mode. Defaults to :obj:`False`
        environment (Dict[str, str]): Env variables for the docker run command. :obj:`optional`
        extra_commands (str): Command added behind the normal command. :obj:`optional`
    """

    image: str = ''
    name: str = ''
    ports: Dict[str, str] = None
    volumes: Dict[str, str] = None
    environment: Dict[str, str] = None
    detached: bool = True
    tty: bool = False
    extra_commands: str = ''

    def commands(self) -> str:
        command = 'docker run'

        if self.detached:
            command += ' -d'

        if self.tty:
            command += ' -t'

        if self.name:
            command += f' --name {self.name}'

        if self.ports:
            for key, value in self.ports.items():
                command += f' -p {key}:{value}'

        if self.volumes:
            for key, value in self.volumes.items():
                command += f' -v {key}:{value}'

        if self.environment:
            for key, value in self.environment.items():
                command += f' -e {key}={value}'

        command += f' {self.extra_commands} {self.image}'

        return command

    def catched_error(self, output: List[str]):
        for line in output:
            if 'Status: Downloaded newer image' in line:
                return True

        return False

    def is_changed(self, output: List[str]):
        for line in output:
            if 'Status: Downloaded newer image' in line:
                return True

        return False
