class MoreHostsWithSameUrlException(Exception):
    """
    This exception is thrown when a specific url for a host is used multiple times in the config file
    """

    msg = "More then one host with teh same url in the config"
