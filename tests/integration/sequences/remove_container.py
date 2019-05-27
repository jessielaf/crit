from crit.executors.utils import CommandExecutor
from crit.sequences import Sequence

print('Docker id: ')
docker_container = input()

sequence = Sequence(
    executors=[
        CommandExecutor(
            command=f'docker container stop {docker_container}',
            sudo=True,
            name='Stop docker container'
        ),
        CommandExecutor(
            command=f'docker container rm {docker_container}',
            sudo=True,
            name='Remove docker container'
        )
    ]
)
