import unittest
import os
from crit.commands import cli
from crit.config import Localhost, config
from crit.exceptions import NoSequenceException, HostNotFoundException
from tests.helpers.config import hosts


work_dir = os.path.dirname(os.path.abspath(__file__))


def get_helper_directory():
    """
    Gets the directory of the test helpers
    """

    return os.path.join(work_dir, 'helpers')


def get_config_file():
    """
    Gets the config file for the tests
    """

    return os.path.join(get_helper_directory(), 'config.py')


class AddConfigTests(unittest.TestCase):
    """
    Tests for the cli function add_config
    """

    def test_specified_config(self):
        """
        If specific config file is given
        """

        cli.add_config(get_config_file())
        self.assertEqual(hosts, config.all_hosts)

    def test_specified_config_wrong(self):
        """
        Right now tests if it throws a file not found error. Will improve this functionality later
        """

        with self.assertRaises(FileNotFoundError):
            cli.add_config(os.path.join(
                get_helper_directory(), 'test/config.py'))

    def test_work_directory_config(self):
        """
        If default is taken
        """

        os.chdir(get_helper_directory())
        cli.add_config('config.py')
        self.assertEqual(hosts, config.all_hosts)
        os.chdir(work_dir)

    def test_work_directory_config_wrong(self):
        """
        Right now tests if it throws a file not found error. Will improve this functionality later
        """

        os.chdir(os.path.dirname(get_helper_directory()))
        with self.assertRaises(FileNotFoundError):
            cli.add_config('config.py')
        os.chdir(work_dir)

    def tearDown(self):
        config.all_hosts = []


class AddHostsTests(unittest.TestCase):
    def test_all_hosts(self):
        """
        If all is given it should be equal to all hosts
        """

        cli.add_hosts('all')
        self.assertEqual(hosts, config.hosts)

    def test_localhost(self):
        """
        If localhost is passed only localhost should be in the registry
        """

        cli.add_hosts('localhost')
        self.assertEqual([Localhost()], config.hosts)

    def test_one_specific_host(self):
        """
        Test if given a specific url
        """

        cli.add_hosts(hosts[0].url)
        self.assertEqual([hosts[0]], config.hosts)

    def test_two_specific_host(self):
        """
        Test if given two specific urls
        """

        cli.add_hosts(hosts[0].url + ',' + hosts[1].url)
        self.assertEqual([hosts[0], hosts[1]], config.hosts)

    def test_wrong_url(self):
        """
        Test if wrong url is given
        """

        with self.assertRaises(HostNotFoundException):
            cli.add_hosts('test')

    @classmethod
    def setUpClass(cls):
        cli.add_config(get_config_file())

    def tearDown(self):
        config.hosts = []


class SequenceFileTests(unittest.TestCase):
    def test_sequence_run(self):
        """
        Test if the sequence runs correctly when everything is given properly
        """

        cli.run_sequence(os.path.join(get_helper_directory(), 'test.py'))

    def test_no_sequence_variable(self):
        """
        Test if the right exception is thrown if the sequence file passed does not contain a sequence variable
        """

        with self.assertRaises(NoSequenceException):
            cli.run_sequence(os.path.join(get_helper_directory(), 'config.py'))

    def test_wrong_file(self):
        """
        Test if file not found is thrown (Will change behaviour)
        """
        with self.assertRaises(FileNotFoundError):
            cli.run_sequence(os.path.join(get_helper_directory(), 'test1.py'))


if __name__ == '__main__':
    unittest.main()