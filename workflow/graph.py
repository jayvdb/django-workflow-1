# -*- coding: utf-8 -*-

__all__ = ['Graph']

class _GraphNode(object):
    ''' Reppresentation of an oriented-graph node.

    Each graph node must have a unique name in the graph where it
    belongs.

    You are free to add whatever other attribute you need by passing
    them as keyword arguments.

    Graph nodes are linked together with lists of incoming and
    outcoming nodes. You can add/remove nodes by calling the
    appropriete methods:

    add_incoming(node)
    add_outcoming(node)
    del_incoming(node)
    del_outcoming(node)

    All This methods must be feeded with a _GraphNode instance which
    is then returned; adding or removing a _GraphNode instance modify
    the current instance and the one involved.

    You can access lists of incoming and outcoming nodes as normal
    dictionaries, but those returned by properties 'outcoming' and
    'incoming' are shallow copies of internal dictionaries.

    A _GraphNode is represented as a dictionary on print.
    '''

    def __init__(self, name, **kwargs):
        '''
        '''
        self.name = name
        for key, val in kwargs.iteritems():
            setattr(self, key, val)
        self.__in = {}
        self.__out = {}

    def __repr__(self):
        return repr(self.__dict__())

    def __dict__(self):
        ret = {
            'name': self.name,
            'outcoming': [elem.name for elem in self.outcoming.itervalues()],
            'incoming': [elem.name for elem in self.incoming.itervalues()],
        }
        return ret

    def __getitem__(self, key):
        return self.outcoming[key]

    @property
    def outcoming(self):
        return self.__out.copy()

    @property
    def incoming(self):
        return self.__in.copy()

    def get(self, key, default=None):
        return self.__out.get(key, default=default)

    def add_incoming(self, node, _first=True):
        if not self.__in.get(node.name, False):
            self.__in[node.name] = node
            if _first:
                node.add_outcoming(self, _first=False)
            return node

    def add_outcoming(self, node, _first=True):
        if not self.__out.get(node.name, False):
            self.__out[node.name] = node
            if _first:
                node.add_incoming(self, _first=False)
            return node

    def del_incoming(self, node, _first=True):
        name = node.name
        try:
            node = self.__in.pop(name)
        except KeyError:
            return None
        if _first:
            node.del_outcoming(self.name, _first=False)
        return node

    def del_outcoming(self, node, _first=True):
        name = node.name
        try:
            node = self.__out.pop(name)
        except KeyError:
            return None
        if _first:
            node.del_incoming(self.name, _first=False)
        return node


class Graph(object):
    ''' An oriented graph.

    An oriented graph is a set of nodes with their respective incoming
    and outcoming lists.

    An oriented graph can be accessed like a normal python dictionary,
    but element(s) can be added or removed just by calling the
    appropriete methods:

    add_node()/add_nodes()
    del_node()/del_nodes()

    When a node is added it is created as an isoleted node, that means
    without any incoming or outcoming arch. To add or remove arch(s)
    use the appropriate methods:

    add_arch()/add_archs()
    del_arch()/del_archs()

    Every Graph method returns a reference to the Graph itself, this
    is to permit a dot notation sequence of Graph updates; example:

    >>> Graph().add_node('one').add_node('two').add_arch('one', 'two')
    or just
    >>> Graph().add_nodes('one', 'two').add_arch('one', 'two)
    Will produce a graph with to nodes linked with an arch.

    '''
    def __init__(self, *names, **kwargs):
        head = None
        if kwargs.has_key('head') and kwargs['head'] in names:
            head = kwargs.pop('head')
        self.__nodes = {'__HEAD__': head}
        for name in names:
            self.add_node(name, **kwargs)
        self.__head = self.__nodes[self.__nodes['__HEAD__']]

    def __repr__(self):
        return repr(self.__dict__())

    def __dict__(self):
        ret = {}
        for key, val in self.__nodes.iteritems():
            try:
                ret[key] = val.__dict__()
            except AttributeError:
                ret[key] = val
        return ret

    def __getitem__(self, key):
        return self.__nodes[key]

    @property
    def head(self):
        return self.__head

    @head.setter
    def head(self, value):
        self.__head = self.__nodes[value]
        self.__nodes['__HEAD__'] = self.__head.name

    def get(self, key, default=None):
        return self.__nodes.get(key, default=default)

    @classmethod
    def parse(cls, wf_dict):
        # build nodes
        head = None
        if wf_dict.has_key('__HEAD__'):
            head = wf_dict.pop('__HEAD__')
        wf = cls()
        for val in wf_dict.values():
            wf = wf.add_node(**val)
        # build archs
        for key, val in wf_dict.iteritems():
            for out_key in val['outcoming']:
                wf.add_arch(key, out_key)
        wf.head = head
        return wf

    def add_node(self, name, head=False, **kwargs):
        node = _GraphNode(name, **kwargs)
        if head:
            self.__head = node
            self.__nodes['__HEAD__'] = node.name
        self.__nodes[node.name] = node
        return self

    def add_nodes(self, *names):
        for name in names:
            self.add_node(name)
        return self

    def del_node(self, name):
        if self.__head.name == name:
            raise RuntimeError("Can not remove head")
        node = self.__nodes.pop(name)
        for node_out in node.outcoming.values():
            node.del_outcoming(node_out)
        for node_in in node.incoming.values():
            node.del_incoming(node_in)
        return self

    def del_nodes(self, *names):
        for name in names:
            self.del_node(name)
        return self

    def add_arch(self, name_out, name_in):
        node_out = self.__nodes[name_out]
        node_in = self.__nodes[name_in]
        node_out.add_outcoming(node_in)
        return self

    def add_archs(self, *archs):
        for arch in archs:
            self.add_arch(arch[0], arch[1])
        return self

    def del_arch(self, name_out, name_in):
        node_out = self.__nodes[name_out]
        node_in = self.__nodes[name_in]
        node_out.del_outcoming(node_in)
        return self

    def del_archs(self, *archs):
        for arch in archs:
            self.del_arch(arch[0], arch[1])
        return self