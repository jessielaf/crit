import unittest
from typing import List
from unittest import mock
from crit.config import Localhost
from crit.executors import Result, MultiExecutor
from crit.executors.result import Status
from crit.executors.utils import UserExecutor, UserAddExecutor, FileExecutor, CommandExecutor
from crit.executors.utils.file_executor import TypeFile


class ExecuteTest(unittest.TestCase):
    username: str = 'admin'
    password: str = 'admin'
    create_home: bool = True
    groups: List[str] = ['test', 'test2']
    ssh_keys: List[str] = ['test_ssh']

    def test_user_exists(self):
        execute_mock = mock.Mock()
        execute_mock.return_value = Result(status=Status.SUCCESS)

        executor = UserExecutor(
            host=Localhost(),
            username=self.username,
            password=self.password,
            groups=self.groups,
            ssh_keys=self.ssh_keys
        )
        executor.execute_executor = execute_mock
        result = executor.execute()

        execute_mock.assert_has_calls([
            mock.call(
                UserAddExecutor(
                    username=self.username,
                    password=self.password,
                    create_home=self.create_home,
                    shell='/bin/bash',
                    groups=self.groups,
                    **executor.get_base_attributes()
                )
            )
        ])

        self.assertEqual(result, Result(status=Status.SUCCESS, message='User is created!'))
        self.assertEqual(execute_mock.call_count, 1)

    def test_with_everything(self):
        execute_mock = mock.Mock()
        execute_mock.return_value = Result(status=Status.CHANGED)

        executor = UserExecutor(
            host=Localhost(),
            username=self.username,
            password=self.password,
            groups=self.groups,
            ssh_keys=self.ssh_keys
        )
        executor.execute_executor = execute_mock
        executor.execute()

        execute_mock.assert_has_calls(self.user_call(executor) + self.calls_before_ssh_keys(executor) + [
            mock.call(
                CommandExecutor(
                    command=f'printf \'{self.ssh_keys}\' | sudo tee /home/{self.username}/.ssh/authorized_keys > /dev/null',
                    **executor.get_base_attributes()
                )
            )
        ] + self.calls_after_ssh_keys(executor))

    def test_without_ssh(self):
        execute_mock = mock.Mock()
        execute_mock.return_value = Result(status=Status.CHANGED)

        executor = UserExecutor(
            host=Localhost(),
            username=self.username,
            password=self.password,
            groups=self.groups
        )
        executor.execute_executor = execute_mock
        executor.execute()

        execute_mock.assert_has_calls(
            self.user_call(executor) +
            self.calls_before_ssh_keys(executor) +
            self.calls_after_ssh_keys(executor)
        )

    def user_call(self, executor: MultiExecutor):
        return [
            mock.call(
                UserAddExecutor(
                    username=self.username,
                    password=self.password,
                    create_home=self.create_home,
                    shell='/bin/bash',
                    groups=self.groups,
                    **executor.get_base_attributes()
                )
            )
        ]

    def calls_before_ssh_keys(self, executor: MultiExecutor):
        return [
            mock.call(
                FileExecutor(
                    path=f'/home/{self.username}/.ssh',
                    type_file=TypeFile.DIRECTORY,
                    **executor.get_base_attributes()
                )
            ),
            mock.call(
                FileExecutor(
                    path=f'/home/{self.username}/.ssh/authorized_keys',
                    type_file=TypeFile.FILE,
                    **executor.get_base_attributes()
                )
            )
        ]

    def calls_after_ssh_keys(self, executor: MultiExecutor):
        return [
            mock.call(
                CommandExecutor(
                    command=f'chown -R {self.username}:{self.username} /home/{self.username}/',
                    **executor.get_base_attributes()
                )
            ),
            mock.call(
                CommandExecutor(
                    command=f'chmod 700 /home/{self.username}/.ssh',
                    **executor.get_base_attributes()
                )
            ),
            mock.call(
                CommandExecutor(
                    command=f'chmod 644 /home/{self.username}/.ssh/authorized_keys',
                    **executor.get_base_attributes()
                )
            )
        ]
