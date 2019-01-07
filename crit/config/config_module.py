from typing import List, Dict
from paramiko import SSHClient
from crit.config import Host


class Config(object):
    """
    The config of the current run

    Attributes:
        hosts (List[Host]): The hosts that are used in the current run
        all_hosts (List[Host]): All the hosts found in the config file
        channels (Dict[str, SSHClient]): The paramiko channels that are matched with the url
        registry (list): The registry of conditional variables in the run
    """

    hosts: List[Host] = []
    all_hosts: List[Host] = []
    channels: Dict[str, SSHClient] = {}
    registry: list = {}

    def __getattr__(self, name):
        """
        Override getattr method so the getattr function will be ran on the private class
        """

        if hasattr(self, name):
            return self.__getattribute__(name)

        return self.run[name]

    def __setattr__(self, name, value):
        if hasattr(self, name):
            super().__setattr__(name, value)
        else:
            self.run[name] = value


config = Config()
