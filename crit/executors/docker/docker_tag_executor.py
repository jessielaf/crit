from dataclasses import dataclass
from crit.executors import SingleExecutor


@dataclass
class DockerTagExecutor(SingleExecutor):
    """
    Pushes a image to a registry

    Args:
        tag (str): The tag which will be tagged to the repository. :obj:`required`
        registry_url (str): The url of the registry which the tag will be ran to. For example :obj:`http://localhost:5000/first_image`. :obj:`required`
    """

    tag: str = ''
    registry_url: str = ''

    def commands(self):
        return f'docker tag {self.tag} {self.registry_url}'
