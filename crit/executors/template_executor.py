import os

from jinja2 import Template

from crit.config import config
from crit.executors import BaseExecutor


class TemplateExecutor(BaseExecutor):
    """
    Creates a file based on a template

    Args:
        src (str): The source of the template. Relative to the work directory
        dest (str): Destination on the host where the template should be put
    """

    src: str
    dest: str

    def __init__(self, src: str, dest: str, *args, **kwargs):
        self.src = src
        self.dest = dest
        super().__init__(*args, **kwargs)

    @property
    def commands(self) -> str:
        template = Template(os.path.join(os.getcwd(), self.src))
        template = template.render(**config)

        return 'echo ' + template + ' > ' + self.dest
