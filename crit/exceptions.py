class ConfigHasNoHostsException(Exception):
    """
    This exception is thrown when the config file does not have a variable host
    """

    msg = 'The config file passed has no hosts defined'


class HostNotFoundException(Exception):
    """
    This exception is thrown when the passed url does not belong to any host
    """

    msg = 'Host is not in config'


class MoreHostsWithSameUrlException(Exception):
    """
    This exception is thrown when a specific url for a host is used multiple times in the config file
    """

    msg = "More then one host with teh same url in the config"


class NoSequenceException(Exception):
    """
    Gets thrown if the sequence file specified does not have sequence variable specified
    """

    msg = 'Sequence file does not contain a sequence variable'
