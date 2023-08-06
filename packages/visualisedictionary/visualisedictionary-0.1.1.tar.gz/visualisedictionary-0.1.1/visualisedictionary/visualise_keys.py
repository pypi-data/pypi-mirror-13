#!/usr/bin/env python
import pygraphviz
'''
    Visualisation of keys of nested dictionaries.
    :author: Alex Warwick Vesztrocy
'''


class KeysGraph(pygraphviz.AGraph):
    def __init__(self, d):
        super(KeysGraph, self).__init__()
        self.graph_attr.update(dpi='300')
        self.node_attr.update(shape="box", style="rounded,filled",
                              fillcolor="beige", color="mediumseagreen")
        self.edge_attr.update(shape="normal", color="lightslateblue",
                              dir="forward")
        self._add_keys(d)
        self.layout(prog='dot')

    def _add_keys(self, d, parent=''):
        if isinstance(d, dict):
            for k in d:
                node_name = parent + '-' + k
                self.add_node(node_name, label=k)
                if(parent != ''):
                    self.add_edge(parent, node_name)
                self._add_keys(d[k], node_name)
