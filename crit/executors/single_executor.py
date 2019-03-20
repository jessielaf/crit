import os
import time
from typing import List
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import paramiko
from crit.executors import BaseExecutor
from paramiko import ChannelFile
from crit.config import Host, config
from crit.exceptions import SingleExecutorFailedException
from .result import Result, Status


@dataclass
class SingleExecutor(BaseExecutor, metaclass=ABCMeta):
    """
    The base executor contains the logic for executing a command

    Args:
        output (str): Output the stdout from the executor. Defaults to :obj:`False`

    Attributes:
        error_lines (List[str]): Strings that will define if a command is an error
    """

    output: bool = False

    # Attributes
    error_lines = ['fail', 'fatal', 'error', 'No such file or directory', 'command not found', 'invalid', 'denied']

    @abstractmethod
    def commands(self) -> str:
        """
        The commands that will be executed

        Returns:
            The commands to run on the server
        """

        pass

    def execute(self, exception_on_error: bool = False, **kwargs) -> Result:
        """
        Executes the command on the host and runs the nested executors if needed

        Args:
            exception_on_error (bool): Throws an exception on error. Can be used in other BaseExecutors
        """

        result = self.run_command()
        self.register_result(result)

        if result.status == Status.FAIL and exception_on_error:
            result.to_table(self.host)
            raise SingleExecutorFailedException(self, result)

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

    def post_executors(self, result: Result) -> List['SingleExecutor']:
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
                return Result(Status.FAIL, message='Pass linux password with -p or pass passwordless_user on hosts!')

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
