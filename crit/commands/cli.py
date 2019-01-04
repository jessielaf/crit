import os
import sys
from importlib import import_module
import click
from importlib.machinery import SourceFileLoader
from crit.exceptions import ConfigHasNoHostsException, NoSequenceException
from crit.config import Localhost, config as config_module
from crit.utils import get_host_by_name


@click.command()
@click.argument('sequence_file')
@click.option('-h', '--hosts', default='all')
@click.option('-c', '--config', default='config.py')
def main(sequence_file, hosts, config):
    add_modules()
    add_config(config)
    add_hosts(hosts)
    run_sequence(sequence_file)


def add_modules():
    """
    This method adds all the directories in work directory to the python path so it can be used as modules
    """

    [sys.path.append(os.path.join(os.getcwd(), x)) for x in os.listdir(os.getcwd())]


def add_config(config):
    config_object = SourceFileLoader("ConfigFile", os.path.join(os.getcwd(), os.path.normpath(
        config))).load_module()

    if hasattr(config_object, 'hosts'):
        config_module.all_hosts = config_object.hosts
    else:
        raise ConfigHasNoHostsException


def add_hosts(hosts):
    if hosts == 'all':
        config_module.hosts = config_module.all_hosts
    else:
        for host in hosts.split(','):
            if hosts == 'localhost' or hosts == '127.0.0.1':
                config_module.hosts.append(Localhost())
            else:
                config_module.hosts.append(get_host_by_name(host))


def run_sequence(sequence_file):
    sequence_object = SourceFileLoader("SequenceScript", os.path.join(os.getcwd(), os.path.normpath(
        sequence_file))).load_module()

    if hasattr(sequence_object, 'sequence'):
        sequence_object.sequence.run()
    else:
        raise NoSequenceException()


if __name__ == "__main__":
    main()
