from definitions import ContainerType
from exception import InvalidConfiguration

class Callback(object):
    def __init__(self, function, **kwargs):
        if function.__code__.co_argcount < 1:
            raise InvalidConfiguration('Callbacks must take at least one argument (node.)')
        self.callable = function
        self.run_count = 0

        self.keys = kwargs.pop('keys', [])
        self.positions = kwargs.pop('keys', ['pre'])
        self.classes = kwargs.pop('keys', [])
        self.containers = kwargs.pop('keys', [])
        self.priority = kwargs.pop('priority', 0)
        self.run_for_orphans = kwargs.pop('run_for_orphans', True)

    def __call__(self, node, *args, **kwargs):
         # exit for enum mode
        if  self.containers and \
            node.container not in self.containers:
            return

        # exit for class
        if  self.classes and \
            node.base_class.__name__ not in self.classes:
            return            

        # exit for key misses
        if  self.keys and \
            node.key not in self.keys:
            return

        # exit for root misses
        if  not self.run_for_orphans and \
            node.is_orphan :
            return

        self.run_count += 1
        return self.callable(node, *args, **kwargs)


class ListCallback(Callback):
    def __init__(self, function, **kwargs):
        super(ListCallback, self).__init__(function, **kwargs)
        self.containers = self.containers or [ContainerType.list]


class DictCallback(Callback):
    def __init__(self, function, **kwargs):
        super(DictCallback, self).__init__(function, **kwargs)
        self.containers = self.containers or [ContainerType.dict]


class ValueCallback(Callback):
    def __init__(self, function, **kwargs):
        super(ValueCallback, self).__init__(function, **kwargs)
        self.containers = self.containers or [ContainerType.value]