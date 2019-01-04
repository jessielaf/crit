class ConfigHasNoHostsException(Exception):
    """
    This exception is thrown when the config file does not have a variable host
    """

    msg = 'The config file passed has no hosts defined'
