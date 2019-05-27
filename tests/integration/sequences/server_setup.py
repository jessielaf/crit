from crit.executors.docker import DockerInstallExecutor
from crit.executors.utils import TemplateExecutor
from crit.sequences import Sequence
from executors.create_users import user_executors

sequence = Sequence(
    executors=[
        DockerInstallExecutor(),
        TemplateExecutor(src='templates/docker_daemon.json', dest='/etc/docker/daemon.json', extra_vars={
            'docker_registry': '192.168.200.101:5000'
        }, tags=['daemon_docker'], sudo=True)
    ] + user_executors
)
