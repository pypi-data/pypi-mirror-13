from exception import InvalidClassConversion
from definitions import (
    RelationshipType, 
    ContainerType,)


class bool_extended(object):
    def __init__(self, v):
        self.val = v 
    def __bool__(self):
        return self.v
    def __str__(self):
        return str(self.val)


class NoneType_extended(object):
    def __bool__(self):
        return False
    def __str__(self):
        return 'None'


class RelationshipMap(object):
    def __init__(self):        
        self.children = []
        self.parents = []
        self.neighbors = [] 


class Node(object):
    __id_counter = 0   

    @classmethod
    def __generate_id(self):
        self.__id_counter += 1
        return self.__id_counter

    def __init__(self, key, val, path, base_class):        
        self.id = self.__generate_id()               
        self.key = key
        self.val = val
        self.path = path
        self.encountered = 1
        self.rel = RelationshipMap()
        
        # TODO: improve this
        if base_class is list:
            self.container = ContainerType.list
        elif base_class is dict:
            self.container = ContainerType.dict
        else:
            self.container = ContainerType.value


    @property
    def is_orphan(self):
        return len(self.rel.parents) < 1

    def parents(self, filters=None, as_value=False, as_generator=False):
        gen = self.__filter_edges(RelationshipType.parent, filters, as_value=as_value)
        if as_generator:
            return gen
        else:
            return [i for i in gen]

    def parent(self, filters=None, as_value=False, as_generator=False):
        parents = self.__filter_edges(RelationshipType.parent, filters, as_value=as_value)
        return parents.next() if parents else None

    def children(self, filters=None, as_value=False, as_generator=False):
        gen = self.__filter_edges(RelationshipType.child, filters, as_value=as_value)
        if as_generator:
            return gen
        else:
            return [i for i in gen]

    def neighbors(self, filters=None, as_value=False, as_generator=False):
        gen = self.__filter_edges(RelationshipType.neighbor, filters, as_value=as_value)
        if as_generator:
            return gen
        else:
            return [i for i in gen]

    def ancestors(self, filters=None, as_value=False, as_generator=False):
        gen = self.__ancestors(filters=filters, as_value=as_value)
        if as_generator:
            return gen
        else:
            return [i for i in gen]

    def orphans(self, filters=None, as_value=False, as_generator=False):
        gen = self.__orphans(filters=filters, as_value=as_value)
        if as_generator:
            return gen
        else:
            return [i for i in gen]

    def siblings(self, filters=None, as_value=False, as_generator=False):
        gen = self.__siblings(filters=filters, as_value=as_value)
        if as_generator:
            return gen
        else:
            return [i for i in gen]

    def descendants(self, filters=None, as_value=False, as_generator=False):
        gen = self.__descendants(filters=filters, as_value=as_value)
        if as_generator:
            return gen
        else:
            return [i for i in gen]

    def add_parent(self, parent):
        if parent not in self.rel.parents:            
            self.rel.parents.append(parent)
            parent.add_child(self)

    def add_child(self, child):
        if child not in self.rel.children:
            self.rel.children.append(child)
            child.add_parent(self)
    
    def add_neighbor(self, neighbor):
        if neighbor not in self.rel.neighbors:
            self.rel.neighbors.append(neighbor)     
            neighbor.add_neighbor(self)       


    # /~~private methods~~/ -----------------------------------------
    def __ancestors(self, filters=None, as_value=False):
        seen = []
        generators = [self.parents()]
        while generators:
            generator = generators.pop()   
            for parent in generator:
                if parent in seen:
                    continue
                seen.append(parent)
                if self.__edge_match(parent, filters=filters):
                    yield parent.val if as_value else parent
                grand_parents = parent.parents()
                if grand_parents:
                    generators.append(grand_parents)

    def __descendants(self, filters=None, as_value=False):
        seen = []
        generators = [self.children()]
        while generators:
            generator = generators.pop()   
            for child in generator:
                if child in seen:
                    continue
                seen.append(child)
                if self.__edge_match(child, filters=filters):
                    yield child.val if as_value else child
                grand_children = child.children()
                if grand_children:
                    generators.append(grand_children)

    def __orphans(self, filters=None, as_value=False):
        for ancestor in self.ancestors(filters=None, as_value=False):
            if ancestor.is_orphan and self.__edge_match(ancestor, filters=filters):
                yield ancestor.val if as_value else ancestor

    def __siblings(self, filters=None, as_value=False, as_generator=False):
        parents = self.parents();
        siblings = [];
        for parent in parents:
            children = parent.children();
            for child in children:
                if child is not self and self.__edge_match(child, filters=filters):
                    yield child.val if as_value else child

    def __filter_edges(self, relationship_type, filters=None, edge_list=None, as_value=False):
        if not edge_list:
            if relationship_type is RelationshipType.child:
                edge_list = self.rel.children
            elif relationship_type is RelationshipType.parent:
                edge_list = self.rel.parents
            else:
                edge_list = self.rel.neighbor
        if filters:            
            for edge in edge_list:
                if self.__edge_match(edge, filters):
                    yield edge.val if as_value else edge
        else:
            for edge in edge_list:
                yield edge.val if as_value else edge

    def __edge_match(self, edge, filters=None):
        if filters:
            for key, val in filters.iteritems():
                v = None
                try:
                    v = edge.val[key]
                except:
                    return False
                if v != val:
                    return False
        return True


class NodeMetadata(object):            
    __node__ = None


class NodeTypeFactory(dict):
    def get(self, val):            
        vclass = val.__class__
        vclass_id = id(vclass)
        wrapper_class = dict.get(self, vclass_id)
        # build and store if it doesn't exist
        if not wrapper_class:
            wrapper_class = type(vclass.__name__+"__node", (NodeMetadata, vclass,),{})
            self[vclass_id] = wrapper_class
        return wrapper_class


class NodeFactory(object):
    __node_list = {}
    __node_type_factory = NodeTypeFactory()   

    @staticmethod
    def convert(key, val, path):
        # if the value is already extended, return the val
        if not getattr(val, '__node__', None):
            base_class = val.__class__
            if base_class is None.__class__:
                val = NoneType_extended()
                wrapper_class = NodeFactory.__node_type_factory.get(val)
                val.__class__ = wrapper_class
            elif base_class is bool:
                val = bool_extended(val)
                wrapper_class = NodeFactory.__node_type_factory.get(val)
                val.__class__ = wrapper_class
            else:
                # first get the wrapper class
                wrapper_class = NodeFactory.__node_type_factory.get(val)
                # overwrite class with new class
                try:
                    val.__class__ = wrapper_class
                except TypeError as e:
                    # failed to do non-user class style, so we have to extend                    
                    new_base_type = type(base_class.__name__+"_extended", (base_class, object), {})                
                    try:
                        val = new_base_type(val)
                        wrapper_class = NodeFactory.__node_type_factory.get(val)
                        val.__class__ = wrapper_class
                    except Exception as e:
                        msg = "Failure to convert class during traversal.\n"
                        msg += "The class `{}` may have been declared in the old style and is not supported by Pilot."
                        raise InvalidClassConversion(msg.format(val.__class__.__name__))

            # now we can init the new node object in val
            val.__node__ = Node(key, val, path, base_class)
        else:
            val.__node__.encountered += 1
        return val


