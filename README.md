# Crit

Infrastructure as actual code

## Why?

This project is created as an alternative for applications like ansible or SaltStack. I ran into the problem of not being able to use actual code many times. So instead of using jinja2 to do conditionals you can actually use `if` and `else`

This project is also more focussed on developers that want to transition to devops activities

## Getting started

We recommend using the [crit-boilerplate](https://github.com/jessielaf/crit-boilerplate)

If you don't want to use the boilerplate we strongly advise to use vagrant for managing your servers.

### Requirements

> The only requirement for crit is that you have python 3.6 installed

### Installing

`pip install crit`

You need two files to start using crit.

#### Config file

The config file contains all the config for crit. This is an example of this config file:

```python3
from crit.config import Host, GeneralConfig

server1 = Host(url='192.168.200.101', ssh_user='vagrant')

config = GeneralConfig(
    hosts=[
        server1
    ]
)
```

- hosts: This variable contains all the hosts you may use for your crit application

#### Sequence file

The sequence file contains a sequence of executors crit will run. This is an example of a sequence file:

```python3
from crit.executors import CommandExecutor
from crit.sequences import Sequence
from example.config import server1

sequence = Sequence(
      executors=[
          CommandExecutor(
              hosts=server1,
              command='ls -a'
          )
      ]
)
```

The sequence variable is mandatory for crit to work.

### Running crit

Now you can run crit by using the crit command `crit sequence.py`

The **first parameter** is the path to the **sequence script** but crit also has some other parameters:

| Short | Long       | Default   | Description                              | Example |
|-------|------------|-----------|------------------------------------------|---------|
| `-h`  | `--hosts`  | all       | The hosts on which the sequence will run | `localhost` |
| `-c`  | `--config` | config.py | The path to the config file of crit      | `config/prod.py` |
| `-t`  | `--tags`   | ''      | Comma separated string with the tags which filters which executors will run | `tag1,tag2` |
| `-st` | `--skip-tags` | '' | Comma separated string with the tags the sequence will skip | `tag3,tag4` |
| `-e` | `--extra-vars` | '' | Key value based variable that will be inserted into the registry | `'key=value key2=value2'` |
| `-p` | `--linux-pass` | '' | Crit will ask for the linux password for the user that is used for ssh'ing | `-p` |
| `-v` | `--verbose` | 0 | Declares the debug level based on how many v's are given | `-v` or `-vv` or `-vvv` ect. |

#### Verbosity
- **1**: Prints the command ran
- **2**: Prints the output & the results of multi executors
- **3**: Shows what is skipped

## Executors

### What is an executor

An executor is a class that contains a command that will run on the server. Your crit config will all be based on executors.

### Executors

Crit comes with some default executors

| Name               | Description                                                  | Doc url |
|--------------------|--------------------------------------------------------------|---------|
| **Abstract Executors**    | | |
| `BaseExecutor`     | The abstract class every executor should inherit. This will often be done by inheriting SingleExecutor or MultiExecutor| [link](https://crit.readthedocs.io/en/latest/crit.executors.base_executor.html)        |
| `SingleExecutor`     | If the executor has a main single command. This is the class that will be inherited | [link](https://crit.readthedocs.io/en/latest/crit.executors.single_executor.html)        |
| `MultiExecutor`     | If an executor relies on multiple single executors you can use a multi executor to run all the executors | [link](https://crit.readthedocs.io/en/latest/crit.executors.multi_executor.html)        |
| **Util executors**  | | |
| `CommandExecutor`  | Executes a command on a server | [link](https://crit.readthedocs.io/en/latest/crit.executors.utils.command_executor.html)        |
| `AptExecutor` | Installs package via apt-get | [link](https://crit.readthedocs.io/en/latest/crit.executors.utils.apt_executor.html)        |
| `UserExecutor` | Creates a linux user | [link](https://crit.readthedocs.io/en/latest/crit.executors.utils.user_executor.html)        |
| `FileExecutor` | Creates a file or directory based on the status | [link](https://crit.readthedocs.io/en/latest/crit.executors.utils.file_executor.html)        |
| `Templa``teExecutor` | Creates a file on the host based on a template               | [link](https://crit.readthedocs.io/en/latest/crit.executors.utils.template_executor.html)        |
| **Docker Executors** | | |
| `DockerInstallExecutor` | Installs docker as a service | [link](https://crit.readthedocs.io/en/latest/crit.executors.premade.docker_install_executor.html) |
| `DockerBuildExecutor` | Build a docker container | [link](https://crit.readthedocs.io/en/latest/crit.executors.docker.docker_build_executor.html) |
| `DockerRunExecutor` | Run a docker container | [link](https://crit.readthedocs.io/en/latest/crit.executors.docker.docker_run_executor.html) |
| `DockerPullExecutor` | Pulls a docker image | [link](https://crit.readthedocs.io/en/latest/crit.executors.docker.docker_pull_executor.html) |
| `DockerPushExecutor` | Pushes a docker image to a registry | [link](https://crit.readthedocs.io/en/latest/crit.executors.docker.docker_push_executor.html) |
| `DockerTagExecutor` | Tags a docker container | [link](https://crit.readthedocs.io/en/latest/crit.executors.docker.docker_tag_executor.html) |
| **Git Executors** | | |
| `GitExecutor` | Runs git clone -> git checkout -> git pull for one repository | [link](https://crit.readthedocs.io/en/latest/crit.executors.premade.git_executor.html) |
| `GitCloneExecutor` | Clones a repository | [link](https://crit.readthedocs.io/en/latest/crit.executors.git.git_clone_executor.html) |
| `GitCheckoutExecutor` | Checks out a certain git branch | [link](https://crit.readthedocs.io/en/latest/crit.executors.git.git_checkout_executor.html) |
| `GitPullExecutor` | Pulls the changes to the repository | [link](https://crit.readthedocs.io/en/latest/crit.executors.git.git_pull_executor.html) |

> All executors can be found in the namespace `crit.executors`

### Creating a custom executor

You can create a standard executor by initiating it. Below is an example of the CommandExecutor

```python3
CommandExecutor(command='ls -a')
```

As you can see this is very limited. This is why you can extend the BaseExecutor to create a totally customizable executor. This is an example how the CommandExecutor is written:

```python3
from dataclasses import dataclass
from crit.executors import SingleExecutor


@dataclass
class CommandExecutor(SingleExecutor):
    command: str = None

    def commands(self) -> str:
        return self.command

```

> All the attributes of a custom executor that is also a @dataclass need to have a default value

## Registry

As mentioned above the config of crit is loaded from a python file. But that is not the only config that crit handles.

Crit supplies a config module that has one especially interesting attribute. This is the **registry** attribute. This attribute is a dict that contains variables that can be used for conditionals in your executor! Each host has it's own registry. So you could access the localhost registry like this `config.registry(repr(Localhost())['registry_key']`

You can import the config via `from crit.config import config`

## Status

Planning

## Tests

We have unit tests and integration tests

### Unit tests

You run them with this command `coverage run -m unittest discover`

### Integration tests

You can run all tests by running `cd /vagrant && sudo python3 setup.py install && cd /vagrant/tests/integration && sh test.sh`


For more info on what is happening see below:

First install crit latest:
```
cd /vagrant && sudo python setup.py install
```

Everything of integration tests is in `/tests/integration/` thus:
```
cd /vagrant/tests/integration
```

1. Install local packages: `crit sequences/local_setup.py -vvv`
2. Setup service server: `crit sequences/service_server.py -vvv`
3. Setup normal server: `crit sequences/server_setup.py -h 192.168.200.102 -vvv`
4. Deploy project: `crit sequences/deploy_project.py -h 192.168.200.102 -vvv`


### Docs

The url to the docs are:

To build the docs:
```
export SPHINX_APIDOC_OPTIONS=members,show-inheritance && sphinx-apidoc -o docs crit -f -e && cp README.md docs/install.md && sphinx-build -b html docs docs/_build
```

## Deployment

Ask [Jessie Liauw A Fong](https://github.com/jessielaf) to for deployment

## Authors

* [Jessie Liauw A Fong](https://github.com/jessielaf)
