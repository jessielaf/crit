import os
import shutil
from typing import Union, List, Tuple
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import paramiko
from termcolor import colored
from crit.config import Host, config
from crit.sequences import Sequence

@dataclass
class BaseExecutor(metaclass=ABCMeta):
    """
    The base executor contains the logic for executing a command

    Args:
        hosts (Union[Host, List[Host]]): The hosts where the BaseExecutor executes the command on. :obj:`optional`
        name (str): The name that will be shown as title. :obj:`optional`
        tags (List[str): The tags decide if the executor will run if tags are passed via the cli. :obj:`optional`
        output (str): Output the stdout from the executor. Defaults to :obj:`False`

    Attributes:
        sequence (Sequence): The sequence that runs the executor
        headers (List[str]): The headers for the output for the cli
        term_width (int): Width of the terminal
    """

    # Args
    hosts: Union[Host, List[Host]] = None
    name: str = None
    tags: List[str] = None
    output: bool = False

    # Attributes
    sequence: Sequence = None
    headers = [
        colored('Host', 'white', attrs=['bold']),
        colored('Status', attrs=['bold']),
        colored('Output', attrs=['bold']),
    ]
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

        hosts = self.hosts or self.sequence.hosts
        results = []

        if isinstance(hosts, Host):
            results.append(self.run_command(hosts))
        elif isinstance(hosts, List):
            for host in hosts:
                results.append(self.run_command(host))

        self.print_table(results)
        print('\n')

    def run_command(self, host: Host) -> Tuple[Host, str, str]:
        """
        Runs a command on a specific host

        Args:
            host (Host): The host where to run the command on

        Returns:
             The stdout from the command in the table format
        """
        stdin, stdout, stderr = self.get_client(host).exec_command(self.commands(host))

        error = stderr.read().decode().split('\n')
        if error != ['']:
            return self.output_to_table(host, error, False)

        return self.output_to_table(host, stdout.read().decode().split('\n'), True)

    @staticmethod
    def get_client(host: Host) -> paramiko.SSHClient:
        """
        Get paramiko client for the host

        Args:
            host: The host for which the client should be returned

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

        line = '=' * self.term_width

        print(line)
        print(colored(self.name or self.__class__.__name__, attrs=['bold']))
        print(line)

    def output_to_table(self, host: Host, output_text: str, status: bool) -> Tuple[Host, str, str]:
        """
        Transforms the output to a tuple that tabulate can handle

        Args:
            host (Host): The host on which the command is ran with
            output_text (str): The output of the str
            status (bool): Status of the command. This means succeeded or not

        Returns:
             The stdout from the command in the table format
        """

        if status:
            color = 'green'
            status_text = 'SUCCESS'
        else:
            self.output = True
            color = 'red'
            status_text = 'FAIL'

        return colored(host, color), colored(status_text, color), (str(output_text) if self.output else '')

    def can_run_tags(self) -> bool:
        """
        Check if the executor can run based on the tags. It prefers tags over skiptags

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

    def print_table(self, results):
        for index, result  in enumerate(results):
            for i, header in enumerate(self.headers):
                if result[i]:
                    print(header + ': ' + result[i])

            if index + 1 != len(results):
                print('-' * self.term_width)
