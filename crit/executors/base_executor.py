from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List, Dict
from crit.config import Host, config, Localhost
from .result import Status, Result


@dataclass
class BaseExecutor(metaclass=ABCMeta):
    """
    Base executor where all other executors are based on

    Args:
        name (str): The name that will be shown as title. :obj:`optional`
        hosts (Union[Host, List[Host]]): The hosts where the BaseExecutor executes the command on. :obj:`optional`
        tags (List[str): The tags decide if the executor will run if tags are passed via the cli. :obj:`optional`
        sudo (bool): Add sudo before the command. Defaults to :obj:`False`
        register (str): Registers the output of the executor to the register. :obj:`optional`
        env (Dict[str, str]): Add the env variables to the command. :obj:`optional`
        chdir (str): Directory in which executor will go before executing its command. :obj:`optional`
        host (Host): DO NOT USE THIS. This is used for the multi executor but should be used with the get_base_attributes function. The host on which the executor is running. :obj:`Not Usable`


    Attributes:
        result (Result): The result of the execution
    """

    name: str = ''
    hosts: List[Host] = None
    tags: List[str] = None
    sudo: bool = False
    register: str = None
    env: Dict[str, str] = None
    chdir: str = None

    # Attributes
    host: Host = None
    result = None

    @abstractmethod
    def execute(self, **kwargs) -> 'Result':
        """
        The function that will execute the tasks of the executor

        Args:
            **kwargs:

        Returns:
            The result of the execution
        """

        pass

    def run(self):
        """
        The function ran when start is called. This is behaviour of thread
        """

        not_in_config = self.not_in_config_hosts()
        if not_in_config:
            return not_in_config

        self.result = self.execute()

        self.register_result()

    def not_in_config_hosts(self):
        """
        Checks if the host of the executor is in config or if it is localhost

        Returns:
            Result or none if the host was correct
        """

        if self.host not in config.hosts and not isinstance(self.host, Localhost):
            return Result(Status.SKIPPING, message='Host is not in global config or passed as argument')

        return None

    def register_result(self):
        """
        Registers the result to the registry based on the host

        Args:
            result (Result): The result of the command
        """

        host_name = repr(self.host)

        if host_name not in config.registry:
            config.registry[host_name] = {}

        config.registry[host_name][self.register] = self.result
