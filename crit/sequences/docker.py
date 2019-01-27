from typing import List
from crit.executors import CommandExecutor, AptExecutor, BaseExecutor


def get_docker_executors() -> List[BaseExecutor]:
    """
    Installs docker on a server. Tags: :obj:`docker_install`

    Returns:
        executors that install vault
    """

    default_kwargs = {'tags': ['docker_install']}
    packages_required = ['apt-transport-https', 'ca-certificates', 'curl', 'software-properties-common']

    update_executor = CommandExecutor(command='apt-get update', sudo=True, name='Update apt-get', **default_kwargs)

    executors = [
        update_executor,
        CommandExecutor(
            name='Upgrade apt-get',
            command='apt-get -y upgrade',
            sudo=True,
            **default_kwargs
        )
    ]

    for package in packages_required:
        executors.append(AptExecutor(package=package, name='install ' + package, **default_kwargs))

    executors += [
        CommandExecutor(
            name='Add docker apt-key',
            sudo=True,
            command='curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -',
            **default_kwargs
        ),
        CommandExecutor(
            name='Add docker repository',
            sudo=True,
            command='add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"',
            **default_kwargs
        ),
        update_executor,
        CommandExecutor(
            name='Add apt-cache policy for docker-ce',
            command='apt-cache policy docker-ce',
            **default_kwargs
        ),
        AptExecutor(
            name='Install docker-ce',
            package='docker-ce',
            **default_kwargs
        )
    ]

    return executors
