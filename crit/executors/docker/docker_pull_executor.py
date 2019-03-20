from dataclasses import dataclass
from crit.executors import SingleExecutor


@dataclass
class DockerPullExecutor(SingleExecutor):
    """
    Pulls an image from a docker registry

    Args:
        image (str): The image that will be pulled. :obj:`required`
        registry_url (str): The url of the registry: :obj:`optional`
        extra_commands (str): The extra commands for the docker pull command. :obj:`optional`
    """

    image: str = ''
    registry_url: str = ''
    extra_commands: str = ''

    def commands(self):
        command = 'docker pull '

        if self.extra_commands:
            command += self.extra_commands + ' '

        # Add registry url to the image
        if self.registry_url:
            command += self.registry_url + '/'

        # Add image
        command += self.image

        return command
