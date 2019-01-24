from crit.config import Localhost
from crit.executors import CommandExecutor
from crit.sequences import Sequence
from example.config import slave1

sequence = Sequence(
    hosts=[Localhost(), slave1],
    executors=[
        CommandExecutor(
            command='ls -a',
            name='Run ls -a'
        ),
        CommandExecutor(
            command='ls -la',
            tags=['list'],
            name='Run ls -l',
            output=True
        )
    ]
)
