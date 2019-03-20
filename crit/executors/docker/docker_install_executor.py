from dataclasses import dataclass
from typing import List
from crit.executors.result import Status
from crit.exceptions import SingleExecutorFailedException
from crit.executors import Result, MultiExecutor
from crit.executors.utils import CommandExecutor, AptExecutor


class DockerAptExecutor(AptExecutor):
    package = 'docker-ce'

    def catched_error(self, output: List[str]):
        for line in output:
            if 'warning: forcing reinstallation' in line:
                return True


@dataclass
class DockerInstallExecutor(MultiExecutor):
    """
    Executor that install docker

    Args:
        sudo (bool): Overwrite sudo from :obj:`BaseExecutor`. Defaults to :obj:`True`

    Attributes:
        packages_required: The required packages to be installed for docker to be installed
    """

    sudo: bool = True

    packages_required = ['apt-transport-https', 'ca-certificates', 'curl', 'software-properties-common']

    def execute(self, **kwargs) -> Result:
        """
        Executors that install docker

        Returns:
            The result of the executors
        """

        update_executor = CommandExecutor(
            command='apt-get update',
            name='Update apt-get',
            **self.get_base_attributes()
        )

        try:
            results = []

            results.append(update_executor.execute(True))
            results.append(CommandExecutor(
                name='Upgrade apt-get',
                command='apt-get -y upgrade',
                env={
                    'DEBIAN_FRONTEND': 'noninteractive'
                },
                **self.get_base_attributes(excluded=['env'])
            ).execute(True))

            for package in self.packages_required:
                results.append(AptExecutor(
                    package=package,
                    name='install ' + package,
                    **self.get_base_attributes()
                ).execute(True))

            results.append(CommandExecutor(
                name='Add docker apt-key',
                command='curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -',
                **self.get_base_attributes()
            ).execute(True))

            results.append(CommandExecutor(
                name='Add docker repository',
                command='add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"',
                **self.get_base_attributes()
            ).execute(True))

            results.append(update_executor.execute(True))

            results.append(CommandExecutor(
                name='Add apt-cache policy for docker-ce',
                command='apt-cache policy docker-ce',
                **self.get_base_attributes()
            ).execute(True))

            results.append(DockerAptExecutor(
                name='Install docker-ce',
                **self.get_base_attributes()
            ).execute(True))

            return self.result_from_executor(results, 'Docker is installed!')
        except SingleExecutorFailedException as e:
            return Result(Status.FAIL, message=e.msg)
