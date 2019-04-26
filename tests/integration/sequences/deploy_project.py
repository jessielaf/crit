from crit.config import Localhost
from crit.executors.docker import DockerBuildExecutor, DockerTagExecutor, DockerPushExecutor, DockerPullExecutor
from crit.executors.git import GitExecutor
from crit.sequences import Sequence

repo = 'effe'
registry_url = '192.168.200.101:5000'
registry_url_image = f'192.168.200.101:5000/{repo}'
directory = f'/vagrant/projects/{repo}'


executors = [
    GitExecutor(
        repository=f'git@github.com:jessielaf/{repo}',
        chdir=directory,
        force=True,
        hosts=[Localhost()]
    ),
    DockerBuildExecutor(
        name='Build docker image',
        tag=repo,
        chdir=directory,
        sudo=True,
        hosts=[Localhost()]
    ),
    DockerTagExecutor(
        name='Tag docker image',
        tag=repo,
        registry_url=registry_url_image,
        sudo=True,
        hosts=[Localhost()]
    ),
    DockerPushExecutor(
        name='Push docker image to registry',
        registry_url=registry_url_image,
        sudo=True,
        hosts=[Localhost()]
    ),
    DockerPullExecutor(
        name='Pulls the image from the private repository',
        registry_url=registry_url,
        image=repo,
        sudo=True
    )
]

sequence = Sequence(
    executors=executors
)
