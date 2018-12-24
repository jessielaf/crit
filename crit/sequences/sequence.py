from dataclasses import dataclass
from typing import Union


@dataclass
class Sequence:
    executors: list
    host: Union[str, list] = 'all'

    def run(self):
        for executor in self.executors:
            executor.sequence = self
            executor.execute()
