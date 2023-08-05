class TreeHandle:

    _futurecall = []
    tree_hierarchy = []

    def get_children(self):
        child_nodes = []

        for child in self.children:
            child_nodes.append(child)

        return child_nodes


    def get_descendants(self):

        for node in self.children:
            TreeHandle.tree_hierarchy.append((self, node))

            if len(node.children) != 0:
                TreeHandle._futurecall.append(node)

        if len(TreeHandle._futurecall) != 0:
            return TreeHandle._futurecall.pop(0).get_descendants() # Recursion until all nodes are processed"""


        tree_hierarchy_copy = TreeHandle.tree_hierarchy.copy()
        TreeHandle.tree_hierarchy.clear()
        return tree_hierarchy_copy

    def __init__(self):
        print("Should not be explicitly create")
        del self


