from crit.config import config, Host
from crit.exceptions import MoreHostsWithSameUrlException, HostNotFoundException


def get_host_by_name(url: str) -> Host:
    """
    Gets the hosts by name from the config

    :param url: The url pas
    :type url: str
    :return: host with the same url as passed as parameter
    :rtype: Host
    """

    host = [host for host in config.all_hosts if host.url == url]

    if len(host) >= 2:
        raise MoreHostsWithSameUrlException
    elif len(host) == 0:
        raise HostNotFoundException

    return host[0]
