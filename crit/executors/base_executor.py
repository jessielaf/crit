import os
import shutil
from typing import Union, List, Tuple
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import paramiko
from termcolor import colored
from crit.config import Host, config
from .result import Result, Status


@dataclass
class BaseExecutor(metaclass=ABCMeta):
    """
    The base executor contains the logic for executing a command

    Args:
        hosts (Union[Host, List[Host]]): The hosts where the BaseExecutor executes the command on. :obj:`optional`
        name (str): The name that will be shown as title. :obj:`optional`
        tags (List[str): The tags decide if the executor will run if tags are passed via the cli. :obj:`optional`
        sudo (bool): Add sudo before the command. Defaults to :obj:`False`
        output (str): Output the stdout from the executor. Defaults to :obj:`False`
        register (str): Registers the output of the executor to the register. :obj:`optional`
        status_nested_executors (str): Defines if the exeutor will run the nested executors. You can choose from :obj:`SUCCESS`, :obj:`CHANGED` & :obj:`FAIL`. Defaults to :obj:`SUCCESS`
        executors (List[BaseExecutor]): The executors to run when status of the executor aligns with :obj:`status_nested_executors`. :obj:`optional`
        never_fail (bool): An executor that does not fail based on the output of the executor. Correlates to get_pty of exec_command paramiko

    Attributes:
        host (Host): The host on which the executor is running
    """

    # Args
    hosts: List[Host] = None
    name: str = None
    tags: List[str] = None
    sudo: bool = False
    output: bool = False
    status_nested_executors: str = 'SUCCESS'
    executors: List['BaseExecutor'] = None
    register: str = None
    never_fail: bool = False

    # Attributes
    host = None

    @abstractmethod
    def commands(self) -> str:
        """
        The commands that will be executed

        Returns:
            The commands to run on the server
        """

        pass

    def execute(self, host: Host) -> Result:
        """
        Executes the command on the host and runs the nested executors if needed

        Args:
            host (Host): The host on which the executor can run
        """

        if host not in config.hosts:
            return Result(Status.SKIPPING, message='Host is not in global config or passed as argument')

        if not self.can_run_tags():
            return Result(Status.SKIPPING, message='Skipping based on tags for this host')

        # Check if the host in in available hosts
        if self.hosts:
            if host in self.hosts:
                self.host = host
            else:
                return Result(Status.SKIPPING, message='Host not in executor\'s host')
        else:
            self.host = host

        result = self.run_command()
        self.register_result(result)

        return result

    def run_command(self) -> Result:
        """
        Runs a command on a specific host

        Args:
            host (Host): The host where to run the command on

        Returns:
             returns the list with the output and if the output was successful or an error
        """

        command = self.commands()

        if self.sudo:
            command = 'sudo ' + command

        stdin, stdout, stderr = self.get_client().exec_command(command, get_pty=self.never_fail)

        error = stderr.read().decode().split('\n')

        if error != [''] and not self.is_warning(error):
            # Checks if the error is just a warning or an actual error
            return Result(Status.FAIL, stdin=command, stdout=error)

        output = stdout.read().decode().split('\n')

        return Result(Status.CHANGED if self.is_changed(output) else Status.SUCCESS, stdin=command, stdout=output, output=self.output)

    def is_warning(self, output: List[str]) -> bool:
        """
        Checks if the output contains warning. If it contains warning and it does NOT contain error or fail the error message is considered a warning

        Args:
            output (List[str]): The output of the command

        Returns:
            If the error page is a warning
        """

        has_warning = False

        for line in output:
            lower_line = line.lower()

            if 'error' in lower_line or 'fail' in lower_line:
                return False
            elif 'warning' in lower_line:
                has_warning = True

        return has_warning

    def is_changed(self, output: List[str]) -> bool:
        """
        Checks if the success text means that the status is changed. This function can be overwritten for custom executors

        Args:
            output (List[str]): A list of strings of the successfull output splitted on \n

        Returns:
            Boolean that indicated if the item has been changed or not. Defaults to :obj:`False`
        """

        return False

    def register_result(self, result: Result):
        host_name = repr(self.host)

        if host_name not in config.registry:
            config.registry[host_name] = {}

        config.registry[host_name][self.register] = result

    def get_client(self) -> paramiko.SSHClient:
        """
        Get paramiko client for the host

        Returns:
            Client which can run the commands
        """

        if self.host.url in config.channels:
            return config.channels[self.host.url]
        else:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=self.host.url, username=self.host.ssh_user, password=self.host.ssh_password,
                           pkey=paramiko.RSAKey.from_private_key_file(os.path.expanduser(self.host.ssh_identity_file)),
                           allow_agent=False, look_for_keys=False)

            config.channels[self.host.url] = client

            return client

    def can_run_tags(self) -> bool:
        """
        Check if the executor can run based on the tags.
        It prefers tags over skiptags

        Returns:
            If the executor can run or not
        """

        if config.tags:
            if not self.tags:
                return False

            in_tags = [tag for tag in self.tags if tag in config.tags]

            return len(in_tags) > 0
        elif config.skip_tags:
            if not self.tags:
                return True

            in_skip_tags = [tag for tag in self.tags if tag in config.skip_tags]

            return len(in_skip_tags) == 0

        return True
