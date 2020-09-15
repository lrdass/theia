from data_structures.utils.auxiliary import Interval
import pprint

class Node:
    left = None
    right = None
    value = None

    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None
    
    def is_leaf(self):
        return self.left is None and self.right is None

    def __str__(self, level=0):
        ret = '\t'*level+repr(self.value)+'\n'
        if not self.is_leaf():
            ret += '{}'.format(self.right.__str__(level+1))
            ret += '{}'.format(self.left.__str__(level+1))
            return ret
        return ret
    
    def __repr__(self):
        return '{}'.format(self.value)

    
 
def build_binary_tree2(points=[]):
    points = sorted(points)
    n = len(points)
    
    mid_point = int((n-1) / 2)
    if n == 1:
        no = Node(points.pop()) 
        return no
    else:
        no = Node(points[mid_point])
        no.left = build_binary_tree2(points[:mid_point+1])
        no.right = build_binary_tree2(points[mid_point+1:])
        return no


def build_binary_tree(points=[]):
    points = sorted(points)
    n = len(points)

    mid_point = int((n-1) / 2)
    if n == 1:
        return {
            "point": points.pop() 
        }
    else:
        no = {
           "split" : points[mid_point],
           "left": build_binary_tree(points[:mid_point+1]),
           "right": build_binary_tree(points[mid_point+1:])
        }
        return no

def search_in_range_1d(tree, range=Interval):
    split_node = find_split_node(tree, range) 
    pass

def find_split_node(node=Node, range=Interval):
    no = node
    while not no.is_leaf and range.x.min<= no.value < range.x.max:
        if range.x.max <= no.value :
            no = node.left
        else:
            no = node.right

    return no

arvore = build_binary_tree2([-10, -8, -7, -5, -2, 2, 5, 6, 10, 4, 55,3,5])
search_in_range_1d(arvore, Interval((-4, 20)))

print(str(arvore))