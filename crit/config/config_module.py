from typing import List, Dict
from paramiko import SSHClient
from crit.config import Host
from crit.config.general_config import GeneralConfig


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
    general_config: GeneralConfig = None
    channels: Dict[str, SSHClient] = {}
    tags: List[str] = []
    skip_tags: List[str] = []
    registry: list = {}
    verbose: int = 0
    sequence: 'crit.sequence.Sequence' = {}

    def get_registered(self, host: Host, item: str):
        return self.registry[repr(host)][item]


config = Config()
