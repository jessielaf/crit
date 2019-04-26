from dataclasses import dataclass
from typing import List
from crit.exceptions import SingleExecutorFailedException
from crit.executors import MultiExecutor
from crit.executors.result import Status
from crit.executors.utils import FileExecutor, CommandExecutor, UserAddExecutor
from crit.executors.utils.file_executor import TypeFile


@dataclass
class UserExecutor(MultiExecutor):
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

    def execute(self, **kwargs):
        try:
            added_user = self.execute_executor(UserAddExecutor(
                username=self.username,
                password=self.password,
                create_home=self.create_home,
                shell=self.shell,
                groups=self.groups,
                **self.get_base_attributes()
            ))

            # Check if the user is created. If it is created or changed only then update everything
            if added_user.status == Status.CHANGED:
                # Creates ssh folder
                self.execute_executor(FileExecutor(
                    path=f'/home/{self.username}/.ssh',
                    type_file=TypeFile.DIRECTORY,
                    **self.get_base_attributes()
                ))

                # Creates the authorized_keys file
                self.execute_executor(FileExecutor(
                    path=f'/home/{self.username}/.ssh/authorized_keys',
                    type_file=TypeFile.FILE,
                    **self.get_base_attributes()
                ))

                # Add ssh keys to the authorized keys
                if self.ssh_keys:
                    self.execute_executor(CommandExecutor(
                        command=f'printf \'{self.ssh_keys}\' | sudo tee /home/{self.username}/.ssh/authorized_keys > /dev/null',
                        **self.get_base_attributes()
                    ))

                # Add right permissions to the home folder of the user
                self.execute_executor(CommandExecutor(
                    command=f'chown -R {self.username} /home/{self.username}/',
                    **self.get_base_attributes()
                ))

                # Permissions for the .ssh folder
                self.execute_executor(CommandExecutor(
                    command=f'chmod 700 /home/{self.username}/.ssh',
                    **self.get_base_attributes()
                ))

                # Permissions for the authorized keys file
                self.execute_executor(CommandExecutor(
                    command=f'chmod 644 /home/{self.username}/.ssh/authorized_keys',
                    **self.get_base_attributes()
                ))

            return self.result_from_executor('User is created!')

        except SingleExecutorFailedException as e:
            return e.result
