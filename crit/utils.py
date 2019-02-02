from crit.config import config, Host
from crit.exceptions import MoreHostsWithSameUrlException, HostNotFoundException


def get_host_by_name(url: str) -> Host:
    """
    Gets the hosts by name from the config

    Args:
        url (str): The url that matches with the host

    Returns:
        Host: host that matches with the url
    """

    host = [host for host in config.general_config.hosts if host.url == url]

    if len(host) >= 2:
        raise MoreHostsWithSameUrlException
    elif len(host) == 0:
        raise HostNotFoundException

    return host[0]
