class HostNotFoundException(Exception):
    """
    This exception is thrown when the passed url does not belong to any host
    """

    msg = 'Host is not in config'
