import os
import click
from importlib.machinery import SourceFileLoader
from crit.sequences import Sequence
from crit.config import Registry, GeneralConfig, Localhost


@click.command()
@click.argument('sequence_file')
@click.option('-h', '--hosts', default='all')
@click.option('-c', '--config', default='config.py')
def main(sequence_file, hosts, config):
    add_config(config)
    create_registry(hosts)
    run_sequence(sequence_file)


def add_config(config):
    config_file = SourceFileLoader("ConfigFile", os.path.join(os.getcwd(), os.path.normpath(
        config))).load_module().hosts

    GeneralConfig(config_file)


def create_registry(hosts):
    host_objects = []
    general_config = GeneralConfig()

    if hosts == 'all':
        host_objects = general_config.get_all()
    else:
        general_config = GeneralConfig()

        for host in hosts.split(','):
            if hosts == 'localhost' or hosts == '127.0.0.1':
                host_objects.append(Localhost)
            else:
                host_objects.append(general_config.get_host_by_name(host))

    Registry({
        'hosts': host_objects
    })


def run_sequence(sequence_file):
    sequence: Sequence = SourceFileLoader("SequenceScript", os.path.join(os.getcwd(), os.path.normpath(
        sequence_file))).load_module().sequence

    sequence.run()


if __name__ == "__main__":
    main()
