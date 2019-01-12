import os
from typing import Union, List

import click
from importlib.machinery import SourceFileLoader
from crit.exceptions import ConfigHasNoHostsException, NoSequenceException
from crit.config import Localhost, config as config_module, config
from crit.utils import get_host_by_name


@click.command()
@click.argument('sequence_file')
@click.option('-h', '--hosts', default='all')
@click.option('-c', '--config', default='config.py')
@click.option('-t', '--tags', default=None)
@click.option('-st', '--skip-tags', default=None)
def main(sequence_file: str, hosts: Union[str, List[str]], config: str, tags: str, skip_tags: str):
    """
    The function run when running the cli

    Args:
        sequence_file (str): The sequence file that will be ran
        hosts (Union[str, List[str]]): The hosts on which crit will run
        config (str): The path to the config file
        tags (str): Comma separated option with the tags which should run
        skip_tags (str): Comma separated option with the tags the sequence should skip
    """

    add_config(config)
    add_hosts(hosts)
    run_sequence(sequence_file)
    add_tags_and_skip_tags(tags, skip_tags)


def add_config(config: str):
    """
    Adding the config to the config module

    Args:
        config (str): The path to the config file
    """

    config_object = SourceFileLoader("ConfigFile", os.path.join(os.getcwd(), os.path.normpath(
        config))).load_module()

    if hasattr(config_object, 'hosts'):
        config_module.all_hosts = config_object.hosts
    else:
        raise ConfigHasNoHostsException


def add_hosts(hosts: Union[str, List[str]]):
    """
    Adding the hosts based on the url

    Args:
        hosts (Union[str, List[str]]): The hosts on which crit will run
    """

    if hosts == 'all':
        config_module.hosts = config_module.all_hosts
    else:
        for host in hosts.split(','):
            if hosts == 'localhost' or hosts == '127.0.0.1':
                config_module.hosts.append(Localhost())
            else:
                config_module.hosts.append(get_host_by_name(host))


def run_sequence(sequence_file: str):
    """
    Run the sequence based on the sequence file

    Args:
        sequence_file (str): The sequence file that will be ran
    """

    sequence_object = SourceFileLoader("SequenceScript", os.path.join(os.getcwd(), os.path.normpath(
        sequence_file))).load_module()

    if hasattr(sequence_object, 'sequence'):
        sequence_object.sequence.run()
    else:
        raise NoSequenceException()


def add_tags_and_skip_tags(tags, skip_tags):
    config.tags = tags.split(',') if tags else []
    config.skip_tags = skip_tags.split(',') if skip_tags else []


if __name__ == "__main__":
    main()
