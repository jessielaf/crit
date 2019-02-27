from dataclasses import dataclass
from crit.executors import SingleExecutor


@dataclass
class CommandExecutor(SingleExecutor):
    """
    An executor for a single command

    Args:
        command (str): The command to be executed. :obj:`required`
    """
    command: str = None

    def commands(self) -> str:
        return self.command
