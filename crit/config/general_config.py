from typing import List
from dataclasses import dataclass
from hvac import Client

from crit.config import Host


@dataclass
class GeneralConfig:
    hosts: List[Host]
    vault: Client = None
