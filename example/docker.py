from crit.sequences import Sequence, get_docker_executors
from example.config import slave1

sequence = Sequence(
    hosts=slave1,
    executors=get_docker_executors()
)
