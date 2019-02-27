from dataclasses import dataclass
from crit.executors import SingleExecutor


@dataclass
class DockerPushExecutor(SingleExecutor):
    """
    Tags a image to a registry

    Args:
        registry_url (str): The url that will be pushed. For example :obj:`http://localhost:5000/first_image`. :obj:`required`
    """

    registry_url: str = ''

    def commands(self):
        return f'docker push {self.registry_url}'
