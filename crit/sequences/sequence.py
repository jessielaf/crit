from dataclasses import dataclass
from typing import Union, List
from crit.config import config, Host


@dataclass
class Sequence:
    """
    The sequence that will be ran by the cli command

    Args:
        executors (List[BaseExecutor]): The executors that will be ran in the same order as this list
        hosts (Union[Host, List[Host]]): The hosts on which this sequence will run
    """
    executors: list
    hosts: Union[Host, List[Host]] = None

    def run(self):
        """
        Runs all the executors in this sequence and closes all the channels of the hosts after running the executors
        """
        self.hosts = self.hosts or config.hosts

        for executor in self.executors:
            executor.sequence = self
            executor.execute()

        for name, channel in config.channels.items():
            channel.close()
