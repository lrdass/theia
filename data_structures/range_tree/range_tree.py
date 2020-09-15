import pprint
import math

class Interval:
    class Range:
        def __init__(self, min_value, max_value):
            self.min = min_value
            self.max = max_value     
    x = None
    y = None
    
    def __init__(self, x_range=(-math.inf,math.inf), y_range=(-math.inf,math.inf)):
        self.x = self.Range(min(x_range), max(x_range))
        self.y = self.Range(min(y_range), max(y_range))
    
    def __repr__(self):
        return 'x : [{},{}], y :[{}, {}]'.format(self.x.min, self.x.max, self.y.min, self.y.max)
    
    def __getitem__(self, name):
        return getattr(self, name)
    def __setitem__(self, name, value):
        return setattr(self, name, value)
    def __delitem__(self, name):
        return delattr(self, name)
    def __contains__(self, name):
        return hasattr(self, name)



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
    split = find_split_node(tree, range) 
    inside = [] 

    if split.is_leaf():
        if range.x.max <= split.value <= range.x.min:
            inside.append(split.value)
    else:
        no = split.left
        while not no.is_leaf():
            if range.x.min <= no.value:
                inside.extend(report_subtree(node=no.right))
                no = no.left
            else:
                no = no.right 
        if range.x.min < no.value <= range.x.max:
            inside.append(no.value)

        no = split.right
        while not no.is_leaf():
            if range.x.max > no.value:
                inside.extend(report_subtree(node=no.left))
                no = no.right
            else:
                no = no.left 
        if range.x.min < no.value <= range.x.max:
            inside.append(no.value)
        
    return set(inside)
        

def report_subtree(node=Node, points=[]):
    if node.is_leaf():
        points.append(node.value)
    else:
        report_subtree(node.left, points)
        report_subtree(node.right, points)
    
    return set(points)

def find_split_node(node=Node, range=Interval):
    no = node
    while not no.is_leaf and range.x.max<= no.value  or range.x.min > no.value:
        if range.x.max <= no.value :
            no = node.left
        else:
            no = node.right

    return no

arvore = build_binary_tree2([-10, -8, -7, -5, -2, 2, 5, 6])
print(search_in_range_1d(arvore, Interval((-6, 20))))

# print(str(arvore))