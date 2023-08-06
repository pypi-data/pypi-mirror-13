from node import NodeFactory
from definitions import ContainerType
from exception import (
    InvalidConfiguration, 
    FlightBreak,)
from callback import Callback

class PilotConfig(object):

    def set(self, key, val):
        if key == 'callbacks':
            self.__clear_callbacks()
            requires_sort = False
            while len(val) > 0:
                callback = val.pop()
                for pos in callback.positions:
                    if pos not in ('pre', 'post'):
                        raise InvalidConfiguration("Invalid callback position.")
                    self.callbacks[pos].append(callback)
                    requires_sort = True
            if requires_sort:
                self.__sort_callbacks()
        else:
            if key == 'callback_sort':
                key = '__callback_sort'
            try:
                setattr(self, key, val)
            except:
                raise InvalidConfiguration("'{}' is not a valid Pilot configuration option.".format(k))

    def __sort_callbacks(self):
        sort = {'cmp': self.callback_sort} if self.callback_sort_mode is 1 else {'key': self.callback_sort}
        self.callbacks['pre'] = sorted(self.callbacks['pre'], **sort)
        self.callbacks['post'] = sorted(self.callbacks['post'], **sort)

    def __clear_callbacks(self):
        self.callbacks['pre'] = []
        self.callbacks['post'] = []

    @property
    def callback_sort(self):
        return self.__callback_sort

    structure = "Tree"
    node_visit_limit = 1
    traversal_mode = 'depth'
    run_callbacks = True
    callbacks = {
        'pre': [],
        'post': []
    }    
    callback_sort_mode = 0 # 1 for cmp
    __callback_sort = lambda self, x: x.priority


class Pilot(object):
    def __init__(self, *callbacks, **settings):     
        self.config = PilotConfig()        
        self.configure(*callbacks, **settings)

    def configure(self, *callbacks, **kwargs):
        cbs = []
        if len(callbacks) > 0:
            if 'callbacks' in kwargs:
                raise InvalidConfiguration("You cannot pass a list of callbacks and specify a keyword callback list in the same configuration.")
            for fn in callbacks:
                cbs.append(Callback(fn))
            kwargs['callbacks'] = cbs
        for k, v in kwargs.iteritems():
            self.config.set(k, v)


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