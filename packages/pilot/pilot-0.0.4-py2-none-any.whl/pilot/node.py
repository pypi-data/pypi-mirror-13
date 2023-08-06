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
    children = []
    parents = []
    neighbors = [] 


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
    def is_orphan(self, filters):
        return len(self.rel.parents) < 1

    def parents(self, filters):
        return self.__filter_edges(RelationshipType.parent, filters)

    def parent(self, filters):
        parents = self.__filter_edges(RelationshipType.parent, filters)
        return parents[0] if parents else None

    def children(self, filters):
        return self.__filter_edges(RelationshipType.child, filters)

    def neighbors(self, filters):
        return self.__filter_edges(RelationshipType.neighbor, filters)

    def ancestors(self, filters):
        ancestors = []
        parents = self.parents()
        while parents.length > 0:
            parent = parents.pop()
            if parent in ancestors:
                continue            
            ancestors.append(parent);
            grand_parents = parent.parents();
            if grand_parents:
                parents = parents.extend(grandParents)
        return self.__filter_edges(None, filters, ancestors)

    def orphans(self, filters):
        seen = [];
        orphans = [];
        edges = this.parents().extend(this.neighbors())
        while edges: 
            edge = edges.pop()
            seen.append(edge)
            if edge.is_orphan:
                orphans.append(edge)
            edge_edges = edge.parents().extend(edge.neighbors())
            for edge_edge in edge_edges:
                if edge_edge in seen:
                    edges.append(edge_edge)
        return self.__filter_edges(None, filters, orphans) 

    def siblings(self):
        parents = self.parents();
        siblings = [];
        for parent in parents:
            children = parent.children();
            for child in children:
                if child is not self:
                    siblings.append(child)
        return self.__filter_edges(None, filters, siblings)

    def add_parent(self, node):
        if node not in self.rel.parents:
            self.rel.parents.append(node)
            node.add_child(self)

    def add_child(self, node):
        if node not in self.rel.children:
            self.rel.children.append(node)
            node.add_parent(self)
    
    def add_neighbor(self, node):
        if node not in self.rel.neighbors:
            self.rel.neighbors.append(node)     
            node.add_neighbor(self)       


    # /~~private methods~~/ -----------------------------------------
    def __filter_edges(self, relationship_type, filters, edge_list=None):
        if not edge_list:
            if relationship_type is RelationshipType.child:
                edge_list = self.rel.children
            elif relationship_type is RelationshipType.parent:
                edge_list = self.rel.parents
            else:
                edge_list = self.rel.neighbor
        if config:            
            for edge in edge_list:
                matched_filter = True
                for key, val in filters.iteritems():
                    if key not in edge or edge[key] is not val:
                        matched_filter = False
                        break
                if matched_filter:
                    matched.append(edge)
        else:
            matched = edge_list
        return matched


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
                        msg = "The class `{}` was declared in the old style and is not supported by Walk."
                        msg += " Old style classes must support copying via the class's `__init__` method."
                        raise InvalidClassConversion(msg.format(val.__class__.__name__))

            # now we can init the new node object in val
            val.__node__ = Node(key, val, path, base_class)
        else:
            val.__node__.encountered += 1
        return val


