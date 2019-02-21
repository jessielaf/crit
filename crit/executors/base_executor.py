import os
import time
from typing import List, Dict
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import paramiko
from paramiko import ChannelFile

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
        env (Dict[str, str]): Add the env variables to the command. :obj:`optional`
        chdir (str): Directory in which executor will go before executing its command. :obj:`optional`

    Attributes:
        host (Host): The host on which the executor is running
        error_lines (List[str]): Strings that will define if a command is an error
    """

    # Args
    hosts: List[Host] = None
    name: str = None
    tags: List[str] = None
    sudo: bool = False
    output: bool = False
    register: str = None
    env: Dict[str, str] = None
    chdir: str = None

    # Attributes
    host = None
    error_lines = ['fail', 'fatal', 'error', 'No such file or directory']

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

        if self.env:
            for key, value in self.env.items():
                command = f'{key}="{value}" ' + command

        if self.sudo:
            command = 'sudo ' + command

        # If chdir is defined add it before the command
        if self.chdir:
            command = f'cd {self.chdir} && ' + command

            if self.sudo:
                command = 'sudo ' + command

        client = self.get_client()
        stdin, stdout, stderr = client.exec_command(command, get_pty=True)

        password_correct = self.fill_password(stdin, stdout)

        if password_correct:
            return password_correct

        output = stdout.read().decode().split('\n')

        # Catch the error
        error_in_text = self.error_in_text(output)
        catched_error = self.catched_error(output)

        if error_in_text and not catched_error:
            # Checks if the error is just a warning or an actual error
            return Result(Status.FAIL, stdin=command, stdout=output)

        return Result(Status.CHANGED if self.is_changed(output) else Status.SUCCESS, stdin=command, stdout=output, output=self.output)

    def error_in_text(self, output: List[str]) -> bool:
        """
        Checks if error or fail is in the error output

        Args:
            output (List[str]): The output of the command

        Returns:
            if error or fail is in the output
        """

        for line in output:
            lower_line = line.lower()
            for error_line in self.error_lines:
                if error_line in lower_line:
                    return True

        return False

    def catched_error(self, output: List[str]) -> bool:
        """
        If fail or error is not in the text return this. in default it returns True if warning is in the text

        Args:
            output (List[str]): The output of the command

        Returns:
            If the error is catched
        """

        return False

    def post_executors(self, result: Result) -> List['BaseExecutor']:
        """
        Executors that get ran right after the main executor

        Args:
            result: The result of this executor on a specific host

        Returns:
            The executors to run
        """

        return []

    def is_changed(self, output: List[str]) -> bool:
        """
        Checks if the success text means that the status is changed. This function can be overwritten for custom executors

        Args:
            output (List[str]): A list of strings of the successfull output splitted on \n

        Returns:
            Boolean that indicated if the item has been changed or not. Defaults to :obj:`False`
        """

        return False

    def fill_password(self, stdin: ChannelFile, stdout: ChannelFile) -> Result:
        """
        Here you can read prompts see https://stackoverflow.com/questions/373639/running-interactive-commands-in-paramiko how to

        Args:
            stdin (ChannelFile): The stdin of the command
            stdout (ChannelFile): The output of the task

        Returns:
            Result if it fails else it returns None which means nothing went wrong
        """
        if self.sudo and not self.host.passwordless_user:
            if not config.linux_password:
                return Result(Status.FAIL, message='Pass linux password with -p or pass no_sudo_password on hosts!')

            time.sleep(0.1)

            stdin.write(config.linux_password + '\n')
            stdin.flush()

            # Read the password
            stdout.readline()
            stdout.readline()

            if 'Sorry, try again.' in stdout.readline():
                stdin.write(chr(3))
                stdin.flush()
                return Result(Status.FAIL, message='Incorrect linux password!')

        return None

    def register_result(self, result: Result):
        """
        Registers the result to the registry based on the host

        Args:
            result (Result): The result of the command
        """

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
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.host.url, username=self.host.ssh_user, password=self.host.ssh_password,
                           pkey=paramiko.RSAKey.from_private_key_file(os.path.expanduser(self.host.ssh_identity_file)),
                           allow_agent=False)

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
