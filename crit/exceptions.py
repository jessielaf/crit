class ConfigNotInFileException(Exception):
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


class WrongExtraVarsFormatException(Exception):
    """
    Gets thrown if the sequence file specified does not have sequence variable specified
    """

    msg = 'The format of the extra vars is not correct'


class SingleExecutorFailedException(Exception):
    """
    Gets thrown when you pass throw exception to the execute command of a single executor
    """

    executor: 'BaseExecutor' = None
    result: 'Result' = None

    def __init__(self, executor: 'BaseExecutor', result: 'Result'):
        self.result = result
        self.executor = executor
        self.msg = f'{repr(executor)} failed and execute got throw exception_on_error'


class NotBaseExecutorTypeException(Exception):
    """
    Gets thrown when a executor passed to a sequence or
    """

    msg = 'The executor does not inherit BaseExecutor'
