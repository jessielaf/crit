from crit.executors import CommandExecutor
from crit.sequences import Sequence
from crit.config import Localhost

sequence = Sequence(
    executors=[
        CommandExecutor(
            hosts=Localhost(),
            command='ls'
        )
    ]
)
