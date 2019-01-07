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
from crit.config.host import Host

server1 = Host(url='192.168.200.101', ssh_user='vagrant')

hosts = [
      server1
]
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

| Short | Long       | Default   | Description                              |
|-------|------------|-----------|------------------------------------------|
| `-h`  | `--hosts`  | all       | The hosts on which the sequence will run |
| `-c`  | `--config` | config.py | The path config file of crit             |

## Executors

### What is an executor

An executor is a class that contains a command that will run on the server. Your crit config will all be based on executors.

### Standard executors

Crit comes with some default executors

| Name               | Description                                                  | Doc url |
|--------------------|--------------------------------------------------------------|---------|
| `BaseExecutor`     | The base executor where all the other executors are build on |         |
| `CommandExecutor`  | Executes a command on a server                               |         |
| `TemplateExecutor` | Creates a file on the host based on a template               |         |

> All executors can be found in the namespace `crit.executors`

### Creating a custom executor

You can create a standard executor by initiating it. Below is an example of the CommandExecutor

```python3
CommandExecutor(command='ls -a')
```

As you can see this is very limited. This is why you can extend the BaseExecutor to create a totally customizable executor. This is an example how the CommandExecutor is written:

```python3
from dataclasses import dataclass
from crit.executors import BaseExecutor


@dataclass
class CommandExecutor(BaseExecutor):
    command: str = None
    output: bool = True

    @property
    def commands(self) -> str:
        return self.command

```

> All the attributes of a custom executor that is also a @dataclass need to have a default value

## Registry

As mentioned above the config of crit is loaded from a python file. But that is not the only config that crit handles.

Crit supplies a config module that has one especially interesting attribute. This is the **registry** attribute. This attribute is a dict that contains variables that can be used for conditionals in your executor!

You can import the config via `from crit.config import config`

## Status

Planning

## Tests

Right now we test the cli and the base executor because that is where most of the logic is a.t.m. You can run the tests by running `python3 -m unittest`

### Docs

The url to the docs are:

To build the docs go to the `docs` directory:
```
export SPHINX_APIDOC_OPTIONS=members,show-inheritance
sphinx-apidoc -o . ../crit -f -e
cp ../README.md install.md
sphinx-build -b html . _build
```

## Deployment

Ask [Jessie Liauw A Fong](https://github.com/jessielaf) to for deployment

## Authors

* [Jessie Liauw A Fong](https://github.com/jessielaf)
