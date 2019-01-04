from dataclasses import dataclass
from typing import Union, List
from crit.config import config, Host


@dataclass
class Sequence:
    executors: list
    hosts: Union[Host, List[Host]] = None

    def run(self):
        self.hosts = self.hosts or config.hosts

        for executor in self.executors:
            executor.sequence = self
            executor.execute()

        for name, channel in config.channels.items():
            channel.close()
