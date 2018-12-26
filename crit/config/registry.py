class Registry(object):
    """
    Singleton that has the variables of the current run
    """

    _registry: list = None

    def __new__(cls, registry=None, *args, **kwargs):
        """
        Override the new method so there can only be one instance of this object
        """

        if not cls._registry and registry is not None:
            cls._registry = registry

        return super().__new__(cls)

    def __getattr__(self, name):
        """
        Override getattr method so the getattr function will be ran on the private class
        """

        if name in self._registry:
            return self._registry[name]

        return self.__getattribute__(name)

    def __setattr__(self, name, value):
        self._registry[name] = value

    def reset_for_test(self):
        self.__class__._registry = None
