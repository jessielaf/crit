import json
from crit.sequences import Sequence
from crit.executors.docker import DockerRunExecutor
from hosts import slave1
from sequences.server_setup import sequence as server_setup_sequence

vault_config = {
        'api_addr': 'http://0.0.0.0:8200',
        'backend': {
            'file': {
                'path': '/vault/file'
            }
        },
        'default_lease_ttl': '168h',
        'max_lease_ttl': '720h',
        'ui': True,
        'listener': [{
            'tcp': {
                'address': '0.0.0.0:8200',
                'tls_disable': 1
            }
        }]
    }

sequence = Sequence(
    hosts=[slave1.slave1],
    executors=server_setup_sequence.executors + [
        DockerRunExecutor(
            image='vault server',
            name='Run docker vault',
            tag='vault',
            environment={
                'VAULT_LOCAL_CONFIG': "'" + json.dumps(vault_config) + "'"
            },
            ports={
                8200: 8200
            },
            extra_commands='--cap-add=IPC_LOCK',
            tty=True,
            sudo=True
        ),
        DockerRunExecutor(
            image='registry:2',
            name='Run registry',
            tag='registry',
            ports={
                5000: 5000
            },
            sudo=True
        )
    ]
)
