from crit.executors import CommandExecutor
from crit.sequences import Sequence

sequence = Sequence(
    host='localhost',
    executors=[
        CommandExecutor(
            command='ls setup.py'
        )
    ]
)
