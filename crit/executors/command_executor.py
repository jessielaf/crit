from crit.executors import BaseExecutor


class CommandExecutor(BaseExecutor):
    command: str

    def __init__(self, command: str, *args, **kwargs):
        self.command = command
        super().__init__(*args, **kwargs)

    @property
    def commands(self) -> str:
        return self.command
