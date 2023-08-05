# -*- coding: utf-8 -*-

"""
i3 WM tree Python manipulation convenience
"""

import i3


class i3Node(object):
    """
    Handful representation of an i3 tree node
    """
    # pylint: disable=invalid-name,too-few-public-methods

    def __init__(self, node, parent=None):
        self.raw_node = node
        self.parent = parent
        self.children = []
        self.children_dict = {}
        self.has_focus = self.focused
        self.focused_child = None

        for child_node in self.nodes:
            child_i3_node = i3Node(child_node, self)
            if child_i3_node.has_focus:
                self.has_focus = True
                self.focused_child = child_i3_node
            self.children.append(child_i3_node)
            self.children_dict[child_i3_node.id] = child_i3_node

    def __getattr__(self, attr):
        try:
            return self.raw_node[attr]
        except KeyError:
            raise AttributeError("{} instance has no attribute '{}'".format(
                self.__class__.__name__,
                attr
            ))

    def __getitem__(self, attr):
        return self.raw_node[attr]

    def __contains__(self, attr):
        return attr in self.raw_node

    def filter(self, function=None, **conditions):
        """
        Adapted from i3.filter
        """
        if function:
            try:
                if function(self):
                    return [self]
            except (KeyError, IndexError):
                pass
        else:
            for key, value in conditions.items():
                if key not in self or self[key] != value:
                    break
            else:
                return [self]
        matches = []
        for child in self.children:
            matches.extend(child.filter(function, **conditions))
        return matches

    def __repr__(self):
        return '<{}, "{}">'.format(self.id, self.name)

    def __unicode__(self):
        return '<{}, "{}">'.format(self.id, self.name)


class i3Tree(object):
    """
    Handful representation of an i3 tree
    """
    # pylint: disable=invalid-name,too-few-public-methods

    def __init__(self, tree=None):
        if not tree:
            tree = i3.get_tree()

        self.raw_tree = tree
        self.root = i3Node(self.raw_tree)

    @property
    def focused(self):
        """
        Return the focused container within the i3 tree
        """
        return self.root.filter(focused=True)[0]
