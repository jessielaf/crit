import unittest
import os
from crit.commands import cli
from crit.config import GeneralConfig, Localhost, Registry
from crit.exceptions.host_not_found_exception import HostNotFoundException
from crit.tests.helpers.config import hosts

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
        self.assertEqual(hosts, GeneralConfig().get_all())

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
        self.assertEqual(hosts, GeneralConfig().get_all())
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
        GeneralConfig().reset_for_test()


class CreateRegistryTests(unittest.TestCase):
    def test_all_hosts(self):
        """
        If all is given it should be equal to all hosts
        """

        cli.create_registry('all')
        self.assertEqual(hosts, Registry().hosts)

    def test_localhost(self):
        """
        If localhost is passed only localhost should be in the registry
        """

        cli.create_registry('localhost')
        self.assertEqual([Localhost()], Registry().hosts)

    def test_one_specific_host(self):
        """
        Test if given a specific url
        """

        cli.create_registry(hosts[0].url)
        self.assertEqual([hosts[0]], Registry().hosts)

    def test_two_specific_host(self):
        """
        Test if given two specific urls
        """

        cli.create_registry(hosts[0].url + ',' + hosts[1].url)
        self.assertEqual([hosts[0], hosts[1]], Registry().hosts)

    def test_wrong_url(self):
        """
        Test if wrong url is given
        """

        with self.assertRaises(HostNotFoundException):
            cli.create_registry('test')

    @classmethod
    def setUpClass(cls):
        cli.add_config(get_config_file())

    def tearDown(self):
        Registry().reset_for_test()


if __name__ == '__main__':
    unittest.main()
