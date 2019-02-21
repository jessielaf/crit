import getpass
import unittest
import os
from unittest import mock
from unittest.mock import Mock
from crit.commands import cli
from crit.config import Localhost, config
from crit.exceptions import NoSequenceException, HostNotFoundException, WrongExtraVarsFormatException
from tests.helpers.config import config as general_config


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
        self.assertEqual(general_config.hosts, config.general_config.hosts)

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
        self.assertEqual(general_config.hosts, config.general_config.hosts)
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
        self.assertEqual(general_config.hosts + [Localhost()], config.hosts)

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

        cli.add_hosts(general_config.hosts[0].url)
        self.assertEqual([general_config.hosts[0], Localhost()], config.hosts)

    def test_two_specific_host(self):
        """
        Test if given two specific urls
        """

        cli.add_hosts(general_config.hosts[0].url + ',' + general_config.hosts[1].url)
        self.assertEqual([general_config.hosts[0], general_config.hosts[1], Localhost()], config.hosts)

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
    @mock.patch('crit.sequences.Sequence')
    def test_sequence_run(self, sequence_mock):
        """
        Test if the sequence runs correctly when everything is given properly
        """

        config.hosts = [Localhost()]

        run_function = Mock()
        sequence_mock.return_value.run = run_function

        self.assertFalse(config.sequence)
        cli.run_sequence(os.path.join(get_helper_directory(), 'test.py'))

        run_function.assert_called_with()
        self.assertTrue(config.sequence)

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


class AddTagsAndSkipTagsTests(unittest.TestCase):
    def test_no_tags_no_skip_tags(self):
        cli.add_tags_and_skip_tags('', '')

        self.assertEqual(config.tags, [])
        self.assertEqual(config.skip_tags, [])

    def test_with_tags_with_skip_tags(self):
        cli.add_tags_and_skip_tags('tag1,tag2', 'tag3,tag4')

        self.assertEqual(config.tags, ['tag1', 'tag2'])
        self.assertEqual(config.skip_tags, ['tag3', 'tag4'])

    def tearDown(self):
        config.tags = []
        config.skip_tags = []


class AddExtraVarsTests(unittest.TestCase):
    def test_no_extra_vars(self):
        cli.add_extra_vars('')
        self.assertEqual(config.registry, {})

    def test_one_extra_vars(self):
        cli.add_extra_vars('key=value')
        self.assertEqual(config.registry, {'key': 'value'})

    def test_multiple_extra_vars(self):
        cli.add_extra_vars('key=value key2=value2')
        self.assertEqual(config.registry, {'key': 'value', 'key2': 'value2'})

    def test_wong_extra_vars(self):
        with self.assertRaises(WrongExtraVarsFormatException):
            cli.add_extra_vars('key=value key2-value2')

    def setUp(self):
        config.registry = {}


class TestSetVerbose(unittest.TestCase):
    def test_set_verbose(self):
        cli.set_verbose(3)
        self.assertEqual(3, config.verbose)


class TestLinuxPassword(unittest.TestCase):
    def test_ask_linux_password(self):
        getpass_mock = Mock()
        getpass_mock.return_value = 'test'
        getpass.getpass = getpass_mock

        cli.ask_linux_password(True)

        self.assertEqual('test', config.linux_password)


if __name__ == '__main__':
    unittest.main()
