from TreeHandle import TreeHandle

# The root node for the GUI tree
class TreeRoot(TreeHandle):

    children = [] # Global since there should only be a single root

    def __init__(self):
        pass
