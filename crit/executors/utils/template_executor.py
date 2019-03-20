import codecs
import os
import re
from dataclasses import dataclass
from jinja2 import Template
from crit.config import config, Host
from crit.executors import SingleExecutor


@dataclass
class TemplateExecutor(SingleExecutor):
    """Creates a file based on a template

    In the templates a few variables are available:

    * `config` (Config): The hosts that are loaded for this sequence
    * `host` (Host): The host where the command is running on
    * `executor` (TemplateExecutor): The executor creating this template

    Args:
        src (str): The source of the template. Relative to the work directory. :obj:`required`
        dest (str): Destination on the host where the template should be put. :obj:`required`
        extra_vars (dict): Dictionary of extra variables you may want to add to the template. :obj:`optional`
    """

    src: str = ''
    dest: str = ''
    extra_vars: dict = None

    def commands(self) -> str:
        """
        It opens the template and renders it via jinja2
        """

        with open(os.path.join(os.getcwd(), self.src), 'r') as content_file:
            template = Template(content_file.read())

            template_output = template.render(
                config=config,
                host=self.host,
                executor=self
            )

            # Adds line endings and escaping quotes
            text = codecs.escape_encode(bytes(template_output, "utf-8"))[0].decode("utf-8").replace("'", "\'")

            pipe = '| '
            if self.sudo:
                pipe += 'sudo '
            pipe += f'tee {self.dest}'

            return 'printf \'' + text + f'\' {pipe}'
