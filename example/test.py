from crit.executors import CommandExecutor
from crit.sequences import Sequence

sequence = Sequence(
    executors=[
        CommandExecutor(
            command='ls'
        )
    ]
)
