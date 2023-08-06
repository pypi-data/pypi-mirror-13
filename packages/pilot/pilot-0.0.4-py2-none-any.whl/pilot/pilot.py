from pprint import pprint
from node import NodeFactory
from definitions import ContainerType
from exception import (
    InvalidConfiguration, 
    FlightBreak,)


class PilotConfig(object):
    structure = "Tree"
    node_visit_limit = 1
    traversal_mode = 'depth'
    run_callbacks = True
    callbacks = {
        'pre': [],
        'post': []
    }


class Pilot(object):
    def __init__(self, **kwargs):
        self.configure(**kwargs)

    def configure(self, **kwargs):
        self.config = getattr(self, 'config', None) or PilotConfig()

        callbacks = kwargs.pop('callbacks', [])
        while len(callbacks) > 0:
            callback = callbacks.pop()
            for pos in callback.positions:
                self.config.callbacks[pos].append(callback)
        
        for k, v in kwargs.iteritems():
            try:
                setattr(self.config, k, v)
            except:
                raise InvalidConfiguration("'{}' is not a valid Pilot configuration option.".format(k))


    def fly(self, obj, rootkey=None, rootpath=None, rootparent=None):
        process_kwargs = {
            'key': rootkey,
            'val': obj,
            'path': rootpath,
            'parent': rootparent
        }
        try:
            return self.__process(**process_kwargs)
        except FlightBreak:
            pass


    def describe(self, data):
        pprint(data)

    @staticmethod
    def halt():
        raise FlightBreak()


    # /~~ private methods ~~/ -----------------------------------------

    def __process(self, queue=None, **kwargs):
       
        # build node
        key = kwargs.pop('key', None)
        val = kwargs.pop('val', None)
        path = kwargs.pop('path', None)        
        converted = NodeFactory.convert(key, val, path)
        node = converted.__node__

        # set parent
        parent = kwargs.pop('parent', None)
        if parent:
            if self.config.structure is 'Tree':
                node.add_parent(parent)
            elif self.config.structure is 'Graph':
                node.add_neighbor(parent)

        # exit if we've visited this node enough
        if self.config.node_visit_limit != -1 and node.encountered > self.config.node_visit_limit:
            return

        # match and run callbacks
        self.__exec_callbacks(node, 0)

        # object processing
        if node.container == ContainerType.dict:
            for k, v in node.val.iteritems():
                process_kwargs = {
                    'key': k,
                    'val': v,
                    'path': None,
                    'parent': node
                }
                if self.config.traversal_mode is 'breadth':
                    queue.append(**process_kwargs)
                else:
                    child = self.__process(**process_kwargs)
                    node.val[k] = child

        # list processing
        elif node.container == ContainerType.list:
            for i, item in enumerate(node.val):
                process_kwargs = {
                    'key': None,
                    'val': item,
                    'path': None,
                    'parent': node
                }
                if self.config.traversal_mode is 'breadth':
                    queue.append(**process_kwargs)
                else:
                    child = self.__process(**process_kwargs)
                    node.val[i] = child

        self.__exec_callbacks(node, 1)

        return node.val


    def __exec_callbacks(self, node, position):
        if not self.config.run_callbacks:
            return
        callbacks = self.__get_callbacks(position)
        for callback in callbacks:
            callback(node)


    def __get_callbacks(self, position):
        if position == 0:
            return self.config.callbacks['pre']
        else:
            return self.config.callbacks['post']