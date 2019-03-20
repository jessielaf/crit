from typing import List
from dataclasses import dataclass
from crit.executors import SingleExecutor


@dataclass
class UserAddExecutor(SingleExecutor):
    """
    Creates a linux user

    Args:
        username (str): The username of the linux user. :obj:`required`
        password (str): The password of the user created via `mkpasswd -m sha-512 salt1234`. :obj:`optional`
        create_home (bool): Creates a home for the user. Defaults to :obj:`True`
        shell (str): Which shell the user uses. Defaults to :obj:`'/bin/bash'`
        groups (List[str]): Groups to add the user to. :obj:`optional`
        sudo (bool): Overwrite sudo from :obj:`BaseExecutor`. Defaults to :obj:`True`
    """

    username: str = ''
    password: str = ''
    create_home: bool = True
    shell: str = '/bin/bash'
    groups: List[str] = None
    sudo: bool = True

    def commands(self):
        add_user_command = f'useradd -s {self.shell}'

        # Add create home for user
        if self.create_home:
            add_user_command += ' -m'

        # Add password
        if self.password:
            add_user_command += f' -p \'{self.password}\''

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
