import pprint

class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

class RangeTree2D:
    def __init__(self, points):
        self.points = points
        self.root = None

    def build(self):
        if len(self.points) <= 1:
            pass
        pass




def build_binary_tree(points=[]):
    def insert(point, tree={}):
        value = tree['value']
        if value:
            if point < value:
                if tree['left'] is None:
                    tree['left'] = {
                        'value': point,
                        'left': None,
                        'right': None,
                    }
                    return tree
                else:
                    tree['left'] = insert(point, tree['left'])
                    return tree
            else:
                if tree['right'] is None:
                    tree['right'] = {
                        'value': point,
                        'left': None,
                        'right': None,
                    }
                    return tree
                else:
                    tree['right'] = insert(point, tree['right'])
                    return tree
        else:
            tree['value'] = point
            return tree
    
    tree = {
        'value': None,
        'left': None,
        'right': None,
    } 
    
    for point in points:
        tree = insert(point, tree)

    return tree

arvore = build_binary_tree([20,10,1,22,9,11,30, 21])

points = [(1,1), (2,3), (4,5), (1,4), (5,2)]




pprint.pprint(arvore)