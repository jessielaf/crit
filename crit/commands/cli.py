import getpass
import os
from typing import Union, List

import click
from importlib.machinery import SourceFileLoader
from crit.exceptions import ConfigNotInFileException, NoSequenceException, WrongExtraVarsFormatException
from crit.config import Localhost, config as config_module, config
from crit.utils import get_host_by_name


@click.command()
@click.argument('sequence_file')
@click.version_option('0.1')
@click.option('-h', '--hosts', default='all', help='The hosts on which the sequence will run')
@click.option('-c', '--config', default='config.py', help='The path to the config file of crit')
@click.option('-t', '--tags', default='', help='Comma separated string with the tags which filters which executors will run')
@click.option('-st', '--skip-tags', default='', help='Comma separated string with the tags the sequence will skip')
@click.option('-e', '--extra-vars', default='', help='Key value based variable that will be inserted into the registry')
@click.option('-v', '--verbose', default=0, count=True, help='Shows the commands that are running')
@click.option('-p', '--linux-pass', is_flag=True, help='Crit will ask for the linux password')
def main(sequence_file: str, hosts: Union[str, List[str]], config: str, tags: str, skip_tags: str, extra_vars: str, verbose: int, linux_pass):
    add_config(config)
    add_hosts(hosts)
    add_tags_and_skip_tags(tags, skip_tags)
    add_extra_vars(extra_vars)
    set_verbose(verbose)
    ask_linux_password(linux_pass)

    # Should always be the last one to run
    run_sequence(sequence_file)


def add_config(config: str):
    """
    Adding the config to the config module

    Args:
        config (str): The path to the config file
    """

    config_object = SourceFileLoader("ConfigFile", os.path.join(os.getcwd(), os.path.normpath(
        config))).load_module()

    if hasattr(config_object, 'config'):
        config_module.general_config = config_object.config
        config_module.general_config.hosts.append(Localhost())
    else:
        raise ConfigNotInFileException


def add_hosts(hosts: Union[str, List[str]]):
    """
    Adding the hosts based on the url

    Args:
        hosts (Union[str, List[str]]): The hosts on which crit will run
    """

    if hosts == 'all':
        config_module.hosts = config_module.general_config.hosts
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
        sequence = sequence_object.sequence
        config.sequence = sequence
        sequence.run()
    else:
        raise NoSequenceException()


def add_tags_and_skip_tags(tags: str, skip_tags: str):
    config.tags = tags.split(',') if tags else []
    config.skip_tags = skip_tags.split(',') if skip_tags else []


def add_extra_vars(extra_vars: str):
    """
    Adds the extra_vars to the registry

    Args:
        extra_vars (str): The extra variables passed via the cli
    """

    if not extra_vars:
        return

    key_values = extra_vars.split(' ')

    for key_value in key_values:
        splitted = key_value.split('=')

        if len(splitted) != 2:
            raise WrongExtraVarsFormatException()

        config.registry[splitted[0]] = splitted[1]


def set_verbose(verbose: int):
    """
    Sets the debug level

    Args:
        verbose (int): Debug level for the sequence
    """

    config.verbose = verbose


def ask_linux_password(linux_pass):
    if linux_pass:
        password = getpass.getpass(prompt='Password for the linux user: ')
        config.linux_password = password


if __name__ == "__main__":
    main()
