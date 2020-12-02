from functools import reduce
import xml.etree.ElementTree as ET
import pprint
import math
from copy import copy
import svgwrite
import random

class Node:
    left = None
    right = None
    value = None
    associated = None

    ## specific for interval tree
    l_associated = None
    r_associated = None

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
    
    # def __getitem__(self, name):
        # return getattr(self, name)
    def __setitem__(self, name, value):
        return setattr(self, name, value)
    def __delitem__(self, name):
        return delattr(self, name)
    def __contains__(self, name):
        return hasattr(self, name)

class Segment(Interval):
    def __init__(self, p1=(0,0), p2=(0,0)):
        super().__init__((p1[0],p2[0]), (p1[1], p2[1]))
        self.p1 = p1
        self.p2 = p2

def create_svg_points(file_name, number_points, size=(200, 200)):
    dwg = svgwrite.Drawing(file_name, size=size)
    dwg.viewbox(-size[0]/2, -size[1]/2, size[0], size[1])
    for n in range(number_points):
        x_rnd = random.randint(-size[0]/2, size[0]/2)
        y_rnd = random.randint(-size[1]/2, size[1]/2)
        dwg.add(dwg.circle(center=(x_rnd, y_rnd), r=2))
    
    x_rnd = random.randint(-size[0]/2, size[0]/2)
    y_rnd = random.randint(-size[1]/2, size[1]/2)
    
    y_size = random.randint(1, (size[1]/2)) 
    x_size = random.randint(1, (size[0]/2))

    x_size = x_size if x_rnd+x_size<= (size[0] / 2) else size[0]/2
    y_size = y_size if y_rnd+y_size<= size[1] / 2 else size[1]/2

    dwg.add(dwg.rect(insert=(x_rnd, y_rnd), size=(x_size, y_size), rx=None, ry=None, fill='none', stroke='red'))

    dwg.save()

# create_svg_points('kkkk.svg', 100)

def circle_to_point(circle):
    circle_dict = circle.attrib
    return (float(circle_dict["cx"]), float(circle_dict["cy"]))

def read_svg_file(svg_file):
    return ET.parse(svg_file)

def colorize_points_inside(points_inside, svg_tree):
    for circle in svg_tree.iter('{http://www.w3.org/2000/svg}circle'):
        point_circle = circle_to_point(circle)
        if point_circle in points_inside:
            circle.attrib['style'] = 'fill:#00ff00' 
    svg_tree.write('teste.svg')


 
def build_binary_tree(points=[]):
    points = sorted(points)
    n = len(points)
    
    mid_point = int((n-1) / 2)
    if n == 1:
        no = Node(points.pop()) 
        return no
    else:
        no = Node(points[mid_point])
        no.left = build_binary_tree(points[:mid_point+1])
        no.right = build_binary_tree(points[mid_point+1:])
        return no

def search_in_range_1d(tree, range=Interval.Range, axis=1):
    split = find_split_node(tree, range)
    inside = [] 

    if split.is_leaf():
        if range.min <= split.value[axis] <= range.max:
            inside.append(split.value)
    else:
        no = split.left
        while not no.is_leaf():
            if range.min <= no.value:
                inside.extend(report_subtree(node=no.right))
                no = no.left
            else:
                no = no.right 
        # aqui ta chegando uma tupla
        if range.min < no.value[axis] <= range.max:
            inside.append(no.value)

        no = split.right
        while not no.is_leaf():
            if range.max > no.value:
                inside.extend(report_subtree(node=no.left))
                no = no.right
            else:
                no = no.left 
        if range.min < no.value[axis] <= range.max:
            inside.append(no.value)
        
    return set(inside)
        

def report_subtree(node=Node, points=[]):
    if node.is_leaf():
        points.append(node.value)
    else:
        report_subtree(node.left, points)
        report_subtree(node.right, points)
    
    return set(points)

def find_split_node(node=Node, range=Interval.Range):
    no = node

    while not no.is_leaf():
        if range.max <= no.value  or range.min > no.value:
            if range.max <= no.value :
                no = no.left
            else:
                no = no.right
        else:
            break

    return no

def build_associated_tree(points=[], axis=1): 
    sorted_points = sorted(points, key=lambda point: point[axis])
    n = len(points)
    
    mid_point = int((n-1) / 2)
    split_value = sorted_points[mid_point][axis]
    if n == 1:
        no = Node(points.pop()) 
        return no
    else:
        no = Node(split_value)
        no.left = build_associated_tree(sorted_points[:mid_point+1])
        no.right = build_associated_tree(sorted_points[mid_point+1:])
        return no
 
def build_2d_range_tree(points=[]):
    y_tree = build_associated_tree(copy(points))

    n = len(points)
    sorted_points = sorted(points, key=lambda point: point[0])
    mid_point = int( (n-1)/2 )

    if n == 1:
        no = Node(points.pop()) 
        no.associated = y_tree
        return no
    else:
        no = Node(sorted_points[mid_point][0])
        no.left = build_2d_range_tree(sorted_points[:mid_point+1])
        no.right = build_2d_range_tree(sorted_points[mid_point+1:])
        no.associated = y_tree
        return no

def search_in_range_2d(tree=Node, query=Interval):
    x_split = find_split_node(tree, query.x)
    inside = []

    if x_split.is_leaf():
        if query.x.min <= x_split.value[0] <= query.x.max:
            inside.append(x_split.value)
    else:
        no = x_split.left
        while not no.is_leaf():
            if query.x.min <= no.value:
                points_inside = search_in_range_1d(no.right.associated, query.y)
                inside.extend(points_inside)
                no = no.left
            else:
                no = no.right
        if query.x.min <= no.value[0] < query.x.max  \
                and query.y.min <= no.value[1] < query.y.max:
            inside.append(no.value)
        
        no = x_split.right
        while not no.is_leaf():
            if query.x.max > no.value:
                points_inside = search_in_range_1d(no.left.associated, query.y)
                inside.extend(points_inside)
                no = no.right
            else:
                no = no.left
        if query.x.min <= no.value[0] <= query.x.max and \
            query.y.min <= no.value[1] <= query.y.max:
            inside.append(no.value)

    return set(inside)


def segments_median(segments=[], axis=0):
    all_points = list(map(lambda segment: [segment.p1, segment.p2], segments))
    all_points_flatten = reduce(lambda acc, curr: acc + curr, all_points)

    all_points_sorted = sorted(all_points_flatten, key=lambda point: point[0]) 

    n = len(all_points_sorted)
    mid = int((n-1)/2)
    return all_points_sorted[mid][0] 

def segments_intersect(segments=[Interval], query=0):
    # segments should be intervals
    i_mid = []
    i_left = []
    i_right = []
    for segment in segments:
        if segment.x.min <= query <= segment.x.max:
            i_mid.extend([segment])
        elif segment.x.max <= query:
            i_left.extend([segment])
        else:
            i_right.extend([segment])
    
    return (i_left, i_mid, i_right)

# horizontal_lines
def build_interval_tree(segments=[]):
    if not len(segments):
        return Node()
    else:
        x_mid = segments_median(segments)
        node = Node(x_mid)
        i_left, i_mid, i_right = segments_intersect(segments, x_mid)
        
        node.l_associated = build_2d_range_tree(list(
            map(lambda segment: segment.p1, i_mid) # get all leftmost points of i_mid
        ))
        node.r_associated = build_2d_range_tree(list(
            map(lambda segment: segment.p2, i_mid) # get all rightmost points of i_mid
        ))

        node.left=build_interval_tree(i_left)
        node.right=build_interval_tree(i_right)

        return node

def query_interval_tree(node=Node(), window=Interval(), inside_segments=[]):
    if not node.is_leaf():
        if window.x.min <= node.value:
            inside_segments.extend(search_in_range_2d(node.l_associated, window)) # search points inside
            inside_segments.extend(search_in_range_2d(node.l_associated, Interval((-math.inf, window.x.min), (window.y.min, window.y.max)))) # points that cross
            query_interval_tree(node.left, window, inside_segments)
        else:
            inside_segments.extend(search_in_range_2d(node.r_associated, window))
            inside_segments.extend(search_in_range_2d(node.r_associated, Interval((window.x.max, math.inf), (window.y.min, window.y.max))))
            query_interval_tree(node.right, window, inside_segments)
    return inside_segments

        

# svg_tree = read_svg_file("new_points.svg")
# points = [circle_to_point(circle) for circle in svg_tree.iter('{http://www.w3.org/2000/svg}circle')] 
# rect_query = svg_tree.find('rect').attrib
# rect_query = svg_tree.find("{http://www.w3.org/2000/svg}rect").attrib

# min_x = float(rect_query['x'])
# max_x = float(rect_query['x']) + float(rect_query['width'])
# min_y = float(rect_query['y'])
# max_y = float(rect_query['y']) + float(rect_query['height'])

# points = [ (-4, 5),(-2,-2),(0,0),(1,1),(1,2),(2,2), (3,1),(3,3),(4,-2),(15,3) ]
# rect_query = Interval((min_x, max_x), (min_y, max_y))
# print(rect_query)

# range_tree = build_2d_range_tree(points)
# print(range_tree)

segments= [
    Segment((0,4), (4,4)),
    Segment((-3,-1), (6, -1)),
    Segment((6, 9), (12, 9)),
    Segment((-8, -5), (-3, -5)),
    Segment((1,1), (3,1)),
]

window = Interval((-1, 3),(4, -4))

interval_tree = build_interval_tree(segments)
print(interval_tree)
points_inside = query_interval_tree(interval_tree, window)
print(points_inside)
# print(str(range_tree))

# points_inside = search_in_range_2d(range_tree, query=rect_query)
# pprint.pprint(points_inside)

# colorize_points_inside(points_inside, svg_tree)

