from TreeHandle import TreeHandle

class TreeNode(TreeHandle):

    # node -> The parent of this node (TreeRoot or TreeNode)
    # name -> Unique identifier for when this node is printed (string)
    def __init__(self, node):
        self.children = []
        node.children.append(self)
