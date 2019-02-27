from typing import List
from dataclasses import dataclass
from crit.executors import SingleExecutor, Result
from crit.executors.result import Status
from .file_executor import FileExecutor, TypeFile
from .command_executor import CommandExecutor


@dataclass
class UserExecutor(SingleExecutor):
    """
    Creates a linux user

    Args:
        username (str): The username of the linux user. :obj:`required`
        password (str): The password of the user created via `mkpasswd -m sha-512 salt1234`. :obj:`optional`
        create_home (bool): Creates a home for the user. Defaults to :obj:`True`
        shell (str): Which shell the user uses. Defaults to :obj:`'/bin/bash'`
        groups (List[str]): Groups to add the user to. :obj:`optional`
        ssh_keys (List[str]): Ssh key for the user. :obj:`optional`
        sudo (bool): Overwrite sudo from :obj:`BaseExecutor`. Defaults to :obj:`True`
    """

    username: str = ''
    password: str = ''
    create_home: bool = True
    shell: str = '/bin/bash'
    groups: List[str] = None
    ssh_keys: List[str] = None
    sudo: bool = True

    def commands(self):
        add_user_command = f'useradd -s {self.shell}'

        # Add password
        if self.password:
            add_user_command += f' -p \'{self.password}\''

        # Add create home for user
        if self.create_home:
            add_user_command += ' -m'

        # Add groups
        if self.groups:
            add_user_command += ' -G '
            for i, group in enumerate(self.groups):
                if i != 0:
                    add_user_command += ','

                add_user_command += group

        return add_user_command + ' ' + self.username

    def catched_error(self, output: List[str]):
        for line in output:
            if f'useradd: user \'{self.username}\' already exists' in line:
                return True

        return super().catched_error(output)

    def is_changed(self, output: List[str]):
        for line in output:
            if f'useradd: user \'{self.username}\' already exists' in line:
                return False

        return True

    def post_executors(self, result: Result):
        if self.ssh_keys and result.status == Status.CHANGED:
            ssh_keys = '\n'.join(self.ssh_keys)

            return [
                FileExecutor(path=f'/home/{self.username}/.ssh', type_file=TypeFile.DIRECTORY, sudo=self.sudo),
                FileExecutor(path=f'/home/{self.username}/.ssh/authorized_keys', type_file=TypeFile.FILE, sudo=self.sudo),
                CommandExecutor(command=f'echo \'{ssh_keys}\' | sudo tee /home/{self.username}/.ssh/authorized_keys > /dev/null', sudo=self.sudo),
                CommandExecutor(command=f'chown -R {self.username}:{self.username} /home/{self.username}/', sudo=self.sudo),
                CommandExecutor(command=f'chmod 700 /home/{self.username}/.ssh', sudo=self.sudo),
                CommandExecutor(command=f'chmod 644 /home/{self.username}/.ssh/authorized_keys', sudo=self.sudo),
            ]

        return []
