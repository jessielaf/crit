from typing import List, Dict
from paramiko import SSHClient
from crit.config import Host


class _Config(object):
    hosts: List[Host] = []
    all_hosts: List[Host] = []
    channels: Dict[str, SSHClient] = {}
    run: list = {}

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


config = _Config()
