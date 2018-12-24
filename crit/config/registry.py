from dataclasses import dataclass


class Registry(object):
    """
    Singleton that handles the info per app
    """

    _instance = None

    @dataclass
    class __Registry:
        """
        Private class for the singleton
        """

        registry: dict

    def __new__(self, *args, **kwargs):
        """
        Override the new method so there can only be one instance of this object
        """

        if not self._instance:
            self._instance = self.__Registry(*args, **kwargs)

        return self._instance

    def __getattr__(self, name):
        """
        Override getattr method so the getattr function will be ran on the private class
        """

        return self._instance.registry[name]

    def set_attribute(self, name, value, overwrite=True):
        if overwrite or name not in self._instance.registry:
            self._instance.registry[name] = value
