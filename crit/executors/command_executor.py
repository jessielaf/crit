from dataclasses import dataclass
from crit.executors import BaseExecutor


@dataclass
class CommandExecutor(BaseExecutor):
    """
    An executor for a single command

    Args:
        command (str): The command to be executed
        output (str) = True: Output the stdout from the executor
    """
    command: str = None
    output: bool = True

    def commands(self, host) -> str:
        return self.command
