import unittest
from crit.executors.docker import DockerRunExecutor


class CommandTest(unittest.TestCase):
    base = 'docker run'
    base_str = f'{base} -d'
    image = 'test'

    def test_command_no_args(self):
        self.assertEqual(DockerRunExecutor(image=self.image).commands(), f'{self.base_str} {self.image}')

    def test_command_tag(self):
        self.assertEqual(DockerRunExecutor(image=self.image, tag='tag').commands(), f'{self.base_str} --name tag {self.image}')

    def test_command_ports(self):
        self.assertEqual(DockerRunExecutor(image=self.image, ports={
            '8000': '8001',
            '5000': '5001'
        }).commands(), f'{self.base_str} -p 8000:8001 -p 5000:5001 {self.image}')

    def test_command_volumes(self):
        self.assertEqual(DockerRunExecutor(image=self.image, volumes={
            '/test': '/1test',
            '/test2': '/1test2'
        }).commands(), f'{self.base_str} -v /test:/1test -v /test2:/1test2 {self.image}')

    def test_command_environment(self):
        self.assertEqual(DockerRunExecutor(image=self.image, environment={
            'TEST': 'value'
        }).commands(), f'{self.base_str} -e TEST=value {self.image}')

    def test_command_detached(self):
        self.assertEqual(DockerRunExecutor(image=self.image, detached=False).commands(), f'{self.base} {self.image}')

    def test_command_tty(self):
        self.assertEqual(DockerRunExecutor(image=self.image, tty=True).commands(), f'{self.base_str} -t {self.image}')

    def test_command_extra_commands(self):
        self.assertEqual(DockerRunExecutor(image=self.image, extra_commands='tag').commands(), f'{self.base_str} tag {self.image}')
