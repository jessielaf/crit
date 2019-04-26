from crit.config import Localhost
from crit.executors.docker import DockerInstallExecutor
from crit.executors.utils import CommandExecutor, TemplateExecutor
from crit.sequences import Sequence

sequence = Sequence(
    hosts=[Localhost()],
    executors=[
        DockerInstallExecutor(),
        CommandExecutor(command='usermod -a -G docker vagrant', sudo=True),
        TemplateExecutor(src='templates/docker_daemon.json', dest='/etc/docker/daemon.json', extra_vars={
            'docker_registry': 'localhost:5000'
        }, tags=['daemon_docker'], sudo=True)
    ]
)
