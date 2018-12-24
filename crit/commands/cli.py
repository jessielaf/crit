import os
import click
from importlib.machinery import SourceFileLoader
from crit.sequences import Sequence
from crit.config import Registry


@click.command()
@click.argument('sequence_file')
@click.option('-h', '--hosts', default='all')
def main(sequence_file, hosts):
    Registry({
        'hosts': 'all' if hosts == 'all' else hosts.split(',')
    })
    sequence: Sequence = SourceFileLoader("sequenceScript", os.path.join(os.getcwd(), os.path.normpath(sequence_file))).load_module().sequence

    sequence.run()


if __name__ == "__main__":
    main()
