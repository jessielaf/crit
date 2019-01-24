import unittest
from crit.config import Localhost
from crit.executors import AptExecutor


class TestAptExecutor(unittest.TestCase):
    def test_install(self):
        """
        Tests if the default works. I am not gonna test each option because it is a waste of time it will be a replica of the code
        """

        executor = AptExecutor(package='curl')

        self.assertEqual('DEBIAN_FRONTEND="noninteractive" apt-get -y install curl', executor.commands(Localhost()))

        # Right text for install
        self.assertTrue(executor.changed(['The following NEW packages will be installed:']))

        # Wrong text for install
        self.assertFalse(executor.changed(['he following NEW packages will be installed:']))
