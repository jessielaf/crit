from crit.executors import CommandExecutor
from crit.sequences import Sequence
from example.config import slave1

sequence = Sequence(
    executors=[
        CommandExecutor(
            hosts=slave1,
            command='ls -a'
        )
    ]
)
