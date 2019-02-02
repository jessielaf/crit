from crit.config import Host, config
from crit.executors import CommandExecutor
from crit.sequences import Sequence, get_docker_executors
from example.config import slave1


# Function that returns
def ls_executor(host: Host):
    return [CommandExecutor(command=config.get_registered("test"), output=True)]


# executors = get_docker_executors()

executors = [
    CommandExecutor(command='echo "echo test"', register='test'),
    ls_executor
]

sequence = Sequence(
    hosts=slave1,
    executors=executors
)
