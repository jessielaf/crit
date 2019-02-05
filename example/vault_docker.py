import json
from crit.config import Host, config
from crit.sequences import Sequence
from crit.executors import DockerRunExecutor


def docker_vault_run(host: Host):
    vault_config = {
        'api_addr': f'http://{host.url}:8200',
        'backend': {
            'file': {
                'path': '/vault/file'
            }
        },
        'default_lease_ttl': '168h',
        'max_lease_ttl': '720h'
    }

    return [
        DockerRunExecutor(
            image='vault server',
            environment={
                'VAULT_LOCAL_CONFIG': f'\'{json.dumps(vault_config)}\''
            },
            ports={
                '8200': '8200'
            },
            extra_commands='--cap-add=IPC_LOCK',
            tty=True,
            register='docker_vault',
            sudo=True
        )
    ]


def print_docker_id(host: Host):
    print(config.get_registered(host, 'docker_vault'))

    return []


sequence = Sequence(
    executors=[
        docker_vault_run,
        print_docker_id
    ]
)
