from dataclasses import dataclass
from crit.executors import BaseExecutor


@dataclass()
class CommandExecutor(BaseExecutor):
    """
    An executor for a single command

    Args:
        command (str): The command to be executed
    """
    command: str = None
    output: bool = True

    @property
    def commands(self) -> str:
        return self.command
