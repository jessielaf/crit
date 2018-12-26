from typing import List
from crit.config import Host
from crit.exceptions import MoreHostsWithSameUrlException
from crit.exceptions.host_not_found_exception import HostNotFoundException


class GeneralConfig(object):
    """
    Singleton that contains the config in the config file
    """

    _hosts: List[Host] = None

    def __new__(cls, hosts: List[Host] = None, *args, **kwargs):
        """
        Override the new method so there can only be one instance of this object
        """

        if not cls._hosts and hosts is not None:
            cls._hosts = hosts

        return super().__new__(cls)

    def get_all(self):
        return self._hosts

    def get_host_by_name(self, url):
        host = [host for host in self._hosts if host.url == url]

        if len(host) >= 2:
            raise MoreHostsWithSameUrlException
        elif len(host) == 0:
            raise HostNotFoundException

        return host[0]

    def reset_for_test(self):
        self.__class__._hosts = None
