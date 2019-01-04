class NoSequenceException(Exception):
    """
    Gets thrown if the sequence file specified does not have sequence variable specified
    """

    msg = 'Sequence file does not contain a sequence variable'
