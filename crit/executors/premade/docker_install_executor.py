from crit.executors.result import Status

from crit.config import Host
from crit.exceptions import SingleExecutorFailedException
from crit.executors import Result, MultiExecutor
from crit.executors.utils import CommandExecutor, AptExecutor


class DockerInstallExecutor(MultiExecutor):
    """
    Executor that install docker

    Args:
        **kwargs: Everything that will be passed to the executors. :obj:`optional`
    """

    kwargs: dict = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def execute(self, host: Host, **kwargs) -> Result:
        """
        Executors that install docker

        Args:
            host (Host): Host on which the executor runs

        Returns:
            The result of the executors
        """

        default_kwargs = {**self.kwargs, **{'tags': ['docker_install']}}
        packages_required = ['apt-transport-https', 'ca-certificates', 'curl', 'software-properties-common']
        update_executor = CommandExecutor(command='apt-get update', sudo=True, name='Update apt-get', **default_kwargs)

        try:
            results = []

            results.append(update_executor.execute(host, True))
            results.append(CommandExecutor(
                name='Upgrade apt-get',
                command='apt-get -y upgrade',
                env={
                    'DEBIAN_FRONTEND': 'noninteractive'
                },
                sudo=True,
                **default_kwargs
            ).execute(host, True))

            for package in packages_required:
                results.append(AptExecutor(package=package, name='install ' + package, **default_kwargs).execute(host, True))

            results.append(CommandExecutor(
                name='Add docker apt-key',
                sudo=True,
                command='curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -',
                **default_kwargs
            ).execute(host, True))

            results.append(CommandExecutor(
                name='Add docker repository',
                sudo=True,
                command='add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"',
                **default_kwargs
            ).execute(host, True))

            results.append(update_executor.execute(host), True)

            results.append(CommandExecutor(
                name='Add apt-cache policy for docker-ce',
                command='apt-cache policy docker-ce',
                **default_kwargs
            ).execute(host, True))

            results.append(AptExecutor(
                name='Install docker-ce',
                package='docker-ce',
                **default_kwargs
            ).execute(host, True))

            return self.result_from_executor(results, 'Docker is installed!')
        except SingleExecutorFailedException as e:
            return Result(Status.FAIL, message=f'Executor with the name {e.executor.name} failed')
