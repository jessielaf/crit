# todo: The clone mock is not working
import unittest
from unittest import mock
from crit.config import Localhost
from crit.executors.docker import DockerInstallExecutor


class ExecuteTest(unittest.TestCase):
    @mock.patch('crit.executors.docker.docker_install_executor.AptExecutor')
    @mock.patch('crit.executors.docker.docker_install_executor.DockerAptExecutor')
    @mock.patch('crit.executors.docker.docker_install_executor.CommandExecutor')
    def test_command(self, command_executor, docker_apt_executor, apt_executor):
        executor = DockerInstallExecutor(host=Localhost())
        executor.execute_executor = mock.Mock()
        executor.execute()

        command_executor.assert_has_calls([
            mock.call(
                command='apt-get update',
                name='Update apt-get',
                **executor.get_base_attributes()
            ),
            mock.call(
                name='Upgrade apt-get',
                command='apt-get -y upgrade',
                env={
                    'DEBIAN_FRONTEND': 'noninteractive'
                },
                **executor.get_base_attributes(excluded=['env'])
            ),
            mock.call(
                name='Add docker apt-key',
                command='curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -',
                **executor.get_base_attributes()
            ),
            mock.call(
                name='Add docker repository',
                command='add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"',
                **executor.get_base_attributes()
            ),
            mock.call(
                name='Add apt-cache policy for docker-ce',
                command='apt-cache policy docker-ce',
                **executor.get_base_attributes()
            )
        ])

        docker_apt_executor.assert_called_with(
            name='Install docker-ce',
            **executor.get_base_attributes()
        )

        apt_calls = []

        for package in executor.packages_required:
            apt_calls += [
                mock.call(
                    package=package,
                    name='install ' + package,
                    **executor.get_base_attributes()
                )
            ]

        apt_executor.assert_has_calls(apt_calls)
