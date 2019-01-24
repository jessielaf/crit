import os
import shutil
from typing import Union, List, Tuple
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import paramiko
from termcolor import colored
from crit.config import Host, config
from .result import Result


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
        term_width (int): Width of the terminal
    """

    # Args
    hosts: Union[Host, List[Host]] = None
    name: str = None
    tags: List[str] = None
    sudo: bool = False
    output: bool = False
    status_nested_executors: str = 'SUCCESS'
    executors: List['BaseExecutor'] = None
    register: str = None
    never_fail: bool = False

    # Attributes
    term_width = shutil.get_terminal_size((80, 20)).columns - 1

    @abstractmethod
    def commands(self, host: Host) -> str:
        """
        The commands that will be executed

        Returns:
            The commands to run on the server
        """

        pass

    def execute(self):
        """
        Execute the commands and prints the table with the output of the executor
        """

        self.print_title()

        if not self.can_run_tags():
            print(colored('Skipping based on tags', 'cyan'))
            return

        hosts = self.hosts or config.sequence.hosts

        if isinstance(hosts, Host):
            self.execute_on_host(hosts)
        elif isinstance(hosts, List):
            for host in hosts:
               self.execute_on_host(host)

    def execute_on_host(self, host: Host):
        """
        Executes the command on the host and runs the nested executors if needed

        Args:
            host: The host on which the executor can run
        """

        # Check if the host in in available hosts
        if host in config.all_hosts:
            result = self.run_command(host)
            self.register_result(host, result)
            status = self.output_to_table(host, result)

            if status == self.status_nested_executors and self.executors:
                for executor in self.executors:
                    executor.execute_on_host(host)

    def run_command(self, host: Host) -> Result:
        """
        Runs a command on a specific host

        Args:
            host (Host): The host where to run the command on

        Returns:
             returns the list with the output and if the output was successful or an error
        """

        command = self.commands(host)

        if self.sudo:
            command = 'sudo ' + command

        stdin, stdout, stderr = self.get_client(host).exec_command(command, get_pty=self.never_fail)

        error = stderr.read().decode().split('\n')

        if error != ['']:
            # Delete host from the hosts to pick from
            config.all_hosts.remove(host)
            return Result(command, error, False)

        return Result(command, stdout.read().decode().split('\n'), True)

    def output_to_table(self, host: Host, result: Result) -> str:
        """
        Prints the output of a command to the terminal in a table format

        Args:
            host (Host): The host on which the command is ran with
            result (Result): The result of the command ran
        """

        if result.success:
            if self.changed(result.stdout):
                color = 'yellow'
                status_text = 'CHANGED'
            else:
                color = 'green'
                status_text = 'SUCCESS'
        else:
            self.output = True
            color = 'red'
            status_text = 'FAIL'

        if config.verbose > 0:
            print(colored('Command: ', 'white', attrs=['bold']) + result.stdin)

        print(colored('Host: ', 'white', attrs=['bold']) + colored(host, color))
        print(colored('Status: ', attrs=['bold']) + colored(status_text, color))

        if self.output:
            print(colored('Output: ', attrs=['bold']) + str(result.stdout))

        print('-' * self.term_width)

        return status_text

    def changed(self, text: List[str]) -> bool:
        """
        Checks if the success text means that the status is changed. This function can be overwritten for custom executors

        Args:
            text (List[str]): A list of strings of the successfull output splitted on \n

        Returns:
            Boolean that indicated if the item has been changed or not. Defaults to :obj:`False`
        """

        return False

    def register_result(self, host: Host, result: Result):
        host_name = repr(host)

        if host_name not in config.registry:
            config.registry[host_name] = {}

        config.registry[host_name][self.register] = result


    @staticmethod
    def get_client(host: Host) -> paramiko.SSHClient:
        """
        Get paramiko client for the host

        Args:
            host (Host): The host for which the client should be returned

        Returns:
            Client which can run the commands
        """

        if host.url in config.channels:
            return config.channels[host.url]
        else:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=host.url, username=host.ssh_user, password=host.ssh_password,
                           pkey=paramiko.RSAKey.from_private_key_file(os.path.expanduser(host.ssh_identity_file)),
                           allow_agent=False, look_for_keys=False)

            config.channels[host.url] = client

            return client

    def print_title(self):
        """
        Prints the title of the executor in the commandline
        """

        if len(config.all_hosts) != 0:
            line = '=' * self.term_width

            print('\n')
            print(line)
            print(colored(self.name or self.__class__.__name__, attrs=['bold']))
            print(line)

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
