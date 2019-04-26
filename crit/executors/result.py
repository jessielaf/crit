import shutil
from enum import Enum, unique
from typing import List
from dataclasses import dataclass
from termcolor import colored
from crit.config import Host, config, Localhost


@unique
class Status(Enum):
    SKIPPING = 'cyan'
    FAIL = 'red'
    SUCCESS = 'green'
    CHANGED = 'yellow'


@dataclass
class Result:
    status: Status
    stdin: str = ''
    stdout: List[str] = None
    message: str = ''
    output: bool = False

    def to_table(self, host: Host = None, name: str = None):
        """
        Prints the output of a command to the terminal in a table format

        Args:
            host (Host): The host on which the command is ran with
            name (str): This can be the name of the executor. This is used in MultiExecutors
        """

        term_width = shutil.get_terminal_size((80, 20)).columns - 1

        if self.status == Status.FAIL and host:
            # Delete host from the hosts to pick from
            if not isinstance(host, Localhost) and host in config.hosts:
                config.hosts.remove(host)
            self.output = True

        if name:
            self.print_line('Name', name)

        if config.verbose > 0:
            self.print_line('Command', self.stdin)

        if host:
            self.print_line('Host', host, self.status.value)

        self.print_line('Status', self.status, self.status.value)

        if self.message:
            self.print_line('Message', self.message)

        if self.output or config.verbose > 1:
            self.print_line('Output', self.stdout)

        print('-' * term_width)

    def print_line(self, key: str, value, color: str=None):
        """
        Prints the line for the key and value

        Args:
            key (str): The key for the table
            value: The value of the table
            color (str): The color of the output text
        """

        print(colored(f'{key}: ', attrs=['bold']) + colored(str(value), color))
