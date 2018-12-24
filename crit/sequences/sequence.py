from dataclasses import dataclass
from typing import Union
from crit.config import Registry


@dataclass
class Sequence:
    executors: list
    hosts: Union[str, list] = None

    def run(self):
        self.hosts = self.hosts or Registry().hosts

        for executor in self.executors:
            executor.sequence = self
            executor.execute()
