import os
from dataclasses import dataclass
from jinja2 import Template
from crit.config import config, Host
from crit.executors import BaseExecutor


@dataclass
class TemplateExecutor(BaseExecutor):
    """Creates a file based on a template

    In the templates a few variables are available:

    * `hosts`: The hosts that are loaded for this sequence
    * `registry`: The registry from the config
    * `all_hosts`: All the hosts from the config file
    * `sequence`: The sequence that runs this executor
    * `current_host`: The host where the command is running on

    Args:
        src (str): The source of the template. Relative to the work directory. :obj:`required`
        dest (str): Destination on the host where the template should be put. :obj:`required`
    """

    src: str = ''
    dest: str = ''

    def commands(self, host: Host) -> str:
        """
        It opens the template and renders it via jinja2
        """

        with open(os.path.join(os.getcwd(), self.src), 'r') as content_file:
            template = Template(content_file.read())

            template_output = template.render(
                registry=config.registry,
                hosts=config.hosts,
                all_hosts=config.all_hosts,
                sequence=config.sequence,
                current_host=host
            )

            return 'echo ' + template_output + ' > ' + self.dest
