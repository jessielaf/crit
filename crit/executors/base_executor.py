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

    Attributes:
        host (Host): The host on which the executor is running
    """

    # Args
    hosts: List[Host] = None
    name: str = None
    tags: List[str] = None
    sudo: bool = False
    output: bool = False
    register: str = None
    env: Dict[str, str] = None

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

        if self.env:
            for key, value in self.env.items():
                command = f'${key}="${value}" ' + command

        if self.sudo:
            command = 'sudo ' + command

        client = self.get_client()
        stdin, stdout, stderr = client.exec_command(command, get_pty=True)

        password_correct = self.fill_password(stdin, stdout)

        if not password_correct:
            return Result(Status.FAIL, message='Incorrect linux password!')

        error = stderr.read().decode().split('\n')
        output = stdout.read().decode().split('\n')

        if error != ['']:
            error_in_text = self.error_in_text(error)
            catched_error = self.catched_error(error)

            if (error_in_text or not catched_error) or (not catched_error and not error_in_text):
                # Checks if the error is just a warning or an actual error
                return Result(Status.FAIL, stdin=command, stdout=error)
            else:
                output = error

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

            if 'error' in lower_line or 'fail' in lower_line:
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

        for line in output:
            lower_line = line.lower()

            if 'warning' in lower_line:
                return True

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

    def fill_password(self, stdin, stdout: ChannelFile):
        """
        Here you can read prompts see https://stackoverflow.com/questions/373639/running-interactive-commands-in-paramiko how to

        Args:
            stdin: The stdin of the command
            stdout: The output of the task

        Returns:
            stdin and out
        """

        if self.sudo and config.linux_password:
            time.sleep(0.1)

            stdin.write(config.linux_password + '\n')
            stdin.flush()

            # Read the password
            stdout.readline()
            stdout.readline()

            if 'Sorry, try again.' in stdout.readline():
                stdin.write(chr(3))
                stdin.flush()
                return False

            return True

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
