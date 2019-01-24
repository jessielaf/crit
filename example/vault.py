from crit.sequences import Sequence, get_vault_executors
from example.config import slave1

sequence = Sequence(
    hosts=slave1,
    executors=get_vault_executors()
)
