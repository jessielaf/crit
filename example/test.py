from crit.config import Localhost
from crit.executors import CommandExecutor
from crit.sequences import Sequence
from example.config import slave1

sequence = Sequence(
    executors=[
        CommandExecutor(
            hosts=Localhost(),
            command='ls -a',
            name='Run ls -a'
        ),
        CommandExecutor(
            hosts=Localhost(),
            command='ls -la',
            tags=['list'],
            name='Run ls -l'
        )
    ]
)
