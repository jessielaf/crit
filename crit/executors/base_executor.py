from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from crit.config import Host
from .result import Result


@dataclass
class BaseExecutor(metaclass=ABCMeta):
    """
    Base executor where all other executors are based on

    Args:
        name (str): The name that will be shown as title. :obj:`optional`
    """

    name: str = ''

    @abstractmethod
    def execute(self, host: Host, **kwargs) -> Result:
        pass
