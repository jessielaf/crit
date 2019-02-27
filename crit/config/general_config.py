from typing import List
from dataclasses import dataclass
from hvac import Client

from crit.config import Host


@dataclass
class GeneralConfig:
    """
    The general config of the crit

    Args:
        hosts (List[Host]): Hosts on which crit can eventually run
        vault (Client): Vault client that will be used for all secrets
    """

    hosts: List[Host]
    vault: Client = None
