from dataclasses import dataclass
from typing import Union, List
from crit.config import Registry, Host


@dataclass
class Sequence:
    executors: list
    hosts: Union[Host, List[Host]] = None

    def run(self):
        self.hosts = self.hosts or Registry().hosts

        for executor in self.executors:
            executor.sequence = self
            executor.execute()
